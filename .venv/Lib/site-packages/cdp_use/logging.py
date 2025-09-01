"""CDP logging configuration following Python library best practices.

By default, cdp-use does not configure any logging. Applications must explicitly
enable CDP logging by calling setup_cdp_logging().

This follows the Python logging best practice that libraries should not configure
logging - they should only emit log records and let applications decide how to
handle them.
"""

import asyncio
import logging
import re
import sys
import time
from typing import Any, Dict, Optional, TextIO


class CDPMessageFilter(logging.Filter):
    """Filter that transforms CDP protocol messages for readability.
    
    This filter processes websockets.client log records and transforms them
    into human-readable CDP protocol messages. It handles:
    - PING/PONG consolidation
    - Message formatting with emojis
    - Suppression of verbose/redundant messages
    - Size display for large messages
    """
    
    def __init__(self):
        super().__init__()
        self.ping_times: Dict[str, float] = {}
        self.ping_timeout_tasks: Dict[str, asyncio.Task] = {}
        
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and transform log records.
        
        Returns:
            True to emit the record (possibly transformed), False to suppress it
        """
        # Only process websockets.client messages
        if record.name != 'websockets.client':
            return True
            
        # Change the logger name to appear as cdp_use
        record.name = 'cdp_use.client'
        
        # Transform the message
        msg = record.getMessage()
        
        # === SPECIAL CASES (suppress or consolidate) ===
        
        # Handle PING/PONG sequences
        if '> PING' in msg:
            match = re.search(r'> PING ([a-f0-9 ]+) \[binary', msg)
            if match:
                ping_data = match.group(1)
                self.ping_times[ping_data] = time.time()
                
                # Schedule timeout warning
                async def check_timeout():
                    await asyncio.sleep(3)
                    if ping_data in self.ping_times:
                        del self.ping_times[ping_data]
                        timeout_logger = logging.getLogger('cdp_use.client')
                        timeout_logger.warning('⚠️ PING not answered by browser... (>3s and no PONG received)')
                
                try:
                    loop = asyncio.get_event_loop()
                    self.ping_timeout_tasks[ping_data] = loop.create_task(check_timeout())
                except RuntimeError:
                    pass
                    
            return False  # Suppress the PING message
            
        elif '< PONG' in msg:
            match = re.search(r'< PONG ([a-f0-9 ]+) \[binary', msg)
            if match:
                pong_data = match.group(1)
                if pong_data in self.ping_times:
                    elapsed = (time.time() - self.ping_times[pong_data]) * 1000
                    del self.ping_times[pong_data]
                    
                    if pong_data in self.ping_timeout_tasks:
                        self.ping_timeout_tasks[pong_data].cancel()
                        del self.ping_timeout_tasks[pong_data]
                    
                    record.msg = f'✔ PING ({elapsed:.1f}ms)'
                    record.args = ()
                    return True
            return False
            
        # Suppress keepalive and EOF messages
        elif ('% sent keepalive ping' in msg or '% received keepalive pong' in msg or 
              '> EOF' in msg or '< EOF' in msg):
            return False
            
        # Connection state messages
        elif '= connection is' in msg:
            if 'CONNECTING' in msg:
                record.msg = '🔗 Connecting...'
            elif 'OPEN' in msg:
                record.msg = '✅ Connected'
            elif 'CLOSING' in msg or 'CLOSED' in msg:
                record.msg = '🔌 Disconnected'
            else:
                msg = msg.replace('= ', '')
                record.msg = msg
            record.args = ()
            return True
            
        elif 'x half-closing TCP connection' in msg:
            record.msg = '👋 Closing our half of the TCP connection'
            record.args = ()
            return True
            
        # === CDP MESSAGE PROCESSING ===
        
        # Parse CDP messages - be flexible with regex matching
        if 'TEXT' in msg:
            # Determine direction
            is_outgoing = '>' in msg[:10]
            
            # Extract and handle size
            size_match = re.search(r'\[(\d+) bytes\]', msg)
            if size_match:
                size_bytes = int(size_match.group(1))
                # Only show size if > 5kb
                size_str = f' [{size_bytes // 1024}kb]' if size_bytes > 5120 else ''
                msg_clean = msg[:msg.rfind('[')].strip() if '[' in msg else msg
            else:
                size_str = ''
                msg_clean = msg
            
            # Extract id and method
            id_match = re.search(r'(?:"id":|id:)\s*(\d+)', msg_clean)
            msg_id = id_match.group(1) if id_match else None
            
            method_match = re.search(r'(?:"method":|method:)\s*"?([A-Za-z.]+)', msg_clean)
            method = method_match.group(1) if method_match else None
            
            # Remove quotes for cleaner output
            msg_clean = msg_clean.replace('"', '')
            
            # Format based on message type
            if is_outgoing and msg_id and method:
                # Outgoing request
                params_match = re.search(r'(?:params:)\s*({[^}]*})', msg_clean)
                params_str = params_match.group(1) if params_match else ''
                
                if params_str == '{}' or not params_str:
                    record.msg = f'🌎 ← #{msg_id}: {method}(){size_str}'
                else:
                    record.msg = f'🌎 ← #{msg_id}: {method}({params_str}){size_str}'
                record.args = ()
                return True
                
            elif not is_outgoing and msg_id:
                # Incoming response
                if 'result:' in msg_clean:
                    result_match = re.search(r'result:\s*({.*})', msg_clean)
                    if result_match:
                        result_str = result_match.group(1)
                        
                        # Clean up and truncate
                        result_str = re.sub(r'},?sessionId:[^}]*}?$', '}', result_str)
                        
                        if result_str == '{}':
                            return False  # Suppress empty results
                        
                        if len(result_str) > 200:
                            result_str = result_str[:200] + '...'
                        
                        record.msg = f'🌎 → #{msg_id}: ↳ {result_str}{size_str}'
                        record.args = ()
                        return True
                        
                elif 'error:' in msg_clean:
                    error_match = re.search(r'error:\s*({[^}]*})', msg_clean)
                    error_str = error_match.group(1) if error_match else 'error'
                    record.msg = f'🌎 → #{msg_id}: ❌ {error_str}{size_str}'
                    record.args = ()
                    return True
                    
            elif not is_outgoing and method:
                # Event
                params_match = re.search(r'params:\s*({.*})', msg_clean)
                params_str = params_match.group(1) if params_match else ''
                
                params_str = re.sub(r'},?sessionId:[^}]*}?$', '}', params_str)
                
                if len(params_str) > 200:
                    params_str = params_str[:200] + '...'
                
                if params_str == '{}' or not params_str:
                    record.msg = f'🌎 → Event: {method}(){size_str}'
                else:
                    record.msg = f'🌎 → Event: {method}({params_str}){size_str}'
                record.args = ()
                return True
        
        # === GENERIC ARROW REPLACEMENT ===
        
        if ' TEXT ' in msg:
            msg = re.sub(r'^>', '🌎 ←', msg)
            msg = re.sub(r'^<', '🌎 →', msg)
            msg = msg.replace(' TEXT ', ' ')
        else:
            msg = re.sub(r'^>', '←', msg)
            msg = re.sub(r'^<', '→', msg)
        
        # Remove quotes
        msg = re.sub(r"['\"]", '', msg)
        
        record.msg = msg
        record.args = ()
        return True


# Global filter instance (created once, reused if setup is called multiple times)
_cdp_filter: Optional[CDPMessageFilter] = None
_filter_attached = False


def setup_cdp_logging(
    level: int = logging.INFO,
    stream: Optional[TextIO] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Enable CDP logging with formatted output.
    
    This function must be called by applications that want CDP logging.
    By default, cdp-use does not configure any logging.
    
    Args:
        level: Logging level (default: INFO)
        stream: Output stream (default: sys.stdout)
        format_string: Log format string (default: '%(levelname)-8s [%(name)s] %(message)s')
        
    Returns:
        The configured cdp_use logger
        
    Example:
        from cdp_use.logging import setup_cdp_logging
        import logging
        
        # Enable CDP logging at DEBUG level
        setup_cdp_logging(level=logging.DEBUG)
        
        # Or with custom formatting
        setup_cdp_logging(
            level=logging.DEBUG,
            format_string='%(asctime)s - %(name)s - %(message)s'
        )
    """
    global _cdp_filter, _filter_attached
    
    # Create filter if not already created
    if _cdp_filter is None:
        _cdp_filter = CDPMessageFilter()
    
    # Attach filter to websockets.client logger (only once)
    if not _filter_attached:
        ws_logger = logging.getLogger('websockets.client')
        ws_logger.addFilter(_cdp_filter)
        _filter_attached = True
    
    # Configure format
    if format_string is None:
        format_string = '%(levelname)-8s [%(name)s] %(message)s'
    
    # Create handler for output
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(logging.Formatter(format_string))
    handler.setLevel(level)
    
    # Configure websockets.client logger
    # This controls whether the filtered messages are emitted
    ws_logger = logging.getLogger('websockets.client')
    ws_logger.setLevel(level)
    ws_logger.addHandler(handler)
    ws_logger.propagate = False  # Don't propagate to root logger
    
    # Configure cdp_use loggers
    cdp_logger = logging.getLogger('cdp_use')
    cdp_logger.setLevel(level)
    cdp_logger.addHandler(handler)
    cdp_logger.propagate = False
    
    # Configure the transformed cdp_use.client logger
    # (this is where filtered messages appear to come from)
    client_logger = logging.getLogger('cdp_use.client')
    client_logger.setLevel(level)
    # Don't add handler here - messages come through websockets.client
    
    return cdp_logger


def disable_cdp_logging() -> None:
    """Disable CDP logging by setting level to CRITICAL.
    
    This effectively silences all CDP-related logs.
    """
    loggers = [
        'websockets.client',
        'cdp_use',
        'cdp_use.client',
        'cdp_use.cdp',
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.CRITICAL)
        logger.handlers.clear()