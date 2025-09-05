"""
Permission management utilities for browser_use.
"""

from typing import List, Optional, Union
from pathlib import Path
import logging
from browser_use.browser.profile import BrowserProfile

logger = logging.getLogger(__name__)

class BrowserPermissionsManager:
    """
    Utility class to manage browser permissions in browser_use.
    
    This class provides helpers to create browser profiles with specific permissions
    and can be used to dynamically grant or revoke permissions during runtime.
    
    Available permissions (from Chrome DevTools Protocol):
    - audioCapture: Access to microphone
    - videoCapture: Access to camera
    - geolocation: Access to location data
    - notifications: Allow sending notifications
    - clipboardReadWrite: Access to clipboard
    - midi: Access to MIDI devices
    - midiSysex: Access to system exclusive MIDI messages
    - sensors: Access to motion/orientation sensors
    - accessibility: Access to accessibility features
    - backgroundSync: Background sync
    - paymentHandler: Payment handler
    - idleDetection: Idle detection API
    - windowManagement: Window management
    """
    
    # List of all available CDP permissions
    # These are the actual permission names used by Chrome DevTools Protocol
    AVAILABLE_PERMISSIONS = [
        'audioCapture',  # microphone
        'videoCapture',  # camera
        'geolocation',
        'notifications',
        'clipboardReadWrite',
        'midi',
        'midiSysex',
        'sensors',
        'accessibility',
        'backgroundSync',
        'paymentHandler', 
        'idleDetection',
        'windowManagement',
        # Additional permissions from the protocol
        'ar',
        'automaticFullscreen',
        'backgroundFetch',
        'cameraPanTiltZoom',
        'capturedSurfaceControl',
        'clipboardSanitizedWrite',
        'displayCapture',
        'durableStorage',
        'handTracking',
        'keyboardLock',
        'localFonts',
        'localNetworkAccess',
        'nfc',
        'periodicBackgroundSync',
        'pointerLock',
        'protectedMediaIdentifier',
        'smartCard',
        'speakerSelection',
        'storageAccess',
        'topLevelStorageAccess',
        'vr',
        'wakeLockScreen', 
        'wakeLockSystem',
        'webAppInstallation',
        'webPrinting'
    ]
    
    # Common presets for convenience
    PRESETS = {
        'default': ['clipboardReadWrite', 'notifications'],
        'voice': ['audioCapture', 'notifications', 'clipboardReadWrite'],  # Voice preset with microphone
        'media': ['audioCapture', 'videoCapture', 'notifications', 'clipboardReadWrite'],  # All media
        'location': ['geolocation', 'notifications', 'clipboardReadWrite'],
        'full': AVAILABLE_PERMISSIONS,
    }
    
    # Mapping for legacy permission names (for backward compatibility)
    PERMISSION_MAP = {
        'microphone': 'audioCapture',
        'camera': 'videoCapture',
        'background-sync': 'backgroundSync',
        'payment-handler': 'paymentHandler',
        'idle-detection': 'idleDetection',
        'window-management': 'windowManagement',
    }
    
    @classmethod
    def create_profile_with_permissions(cls, 
                                     permissions: Union[List[str], str],
                                     user_data_dir: Optional[Union[str, Path]] = None,
                                     headless: bool = False,
                                     **kwargs) -> BrowserProfile:
        """
        Create a BrowserProfile with specific permissions.
        
        Args:
            permissions: List of permission names or a preset name ('default', 'media', 'location', 'full')
            user_data_dir: Path to user data directory for persistence
            headless: Whether to run browser in headless mode
            **kwargs: Additional arguments for BrowserProfile
            
        Returns:
            BrowserProfile: Configured profile with specified permissions
        """
        # If permissions is a string, check if it's a preset
        if isinstance(permissions, str):
            if permissions in cls.PRESETS:
                permission_list = cls.PRESETS[permissions]
            else:
                permission_list = [permissions]
        else:
            permission_list = permissions
            
        # Convert legacy permission names to CDP standard names
        converted_permissions = []
        for perm in permission_list:
            if perm in cls.PERMISSION_MAP:
                logger.info(f"Converting legacy permission name '{perm}' to CDP standard name '{cls.PERMISSION_MAP[perm]}'")
                converted_permissions.append(cls.PERMISSION_MAP[perm])
            else:
                converted_permissions.append(perm)
            
        # Validate permissions
        for perm in converted_permissions:
            if perm not in cls.AVAILABLE_PERMISSIONS:
                logger.warning(f"Warning: '{perm}' is not a standard Chrome DevTools Protocol permission")
                
        # Create and return the profile
        return BrowserProfile(
            user_data_dir=user_data_dir,
            permissions=converted_permissions,
            headless=headless,
            **kwargs
        )
        
    @classmethod
    def create_voice_enabled_profile(cls,
                                 user_data_dir: Optional[Union[str, Path]] = None,
                                 headless: bool = False,
                                 **kwargs) -> BrowserProfile:
        """
        Create a BrowserProfile with microphone permission enabled by default.
        This is a convenience method for voice-enabled applications.
        
        Args:
            user_data_dir: Path to user data directory for persistence
            headless: Whether to run browser in headless mode
            **kwargs: Additional arguments for BrowserProfile
            
        Returns:
            BrowserProfile: Configured profile with microphone permission
        """
        # Use the voice preset which includes microphone permission
        return cls.create_profile_with_permissions(
            permissions='voice',
            user_data_dir=user_data_dir,
            headless=headless,
            **kwargs
        )
    
    @classmethod
    async def grant_permissions(cls, browser_session, 
                              permissions: List[str], 
                              origin: Optional[str] = None):
        """
        Dynamically grant permissions to a running browser session.
        
        Args:
            browser_session: The active browser session
            permissions: List of permissions to grant
            origin: Optional origin to restrict permissions to (e.g. 'https://example.com')
                   If None, permissions are granted to all origins.
        """
        # Convert legacy permission names to CDP standard names
        converted_permissions = []
        for perm in permissions:
            if perm in cls.PERMISSION_MAP:
                logger.info(f"Converting legacy permission name '{perm}' to CDP standard name '{cls.PERMISSION_MAP[perm]}'")
                converted_permissions.append(cls.PERMISSION_MAP[perm])
            else:
                converted_permissions.append(perm)
                
        logger.info(f"Granting permissions: {converted_permissions}" + 
                   (f" for {origin}" if origin else " for all origins"))
        
        try:
            params = {'permissions': converted_permissions}
            if origin:
                params['origin'] = origin
                
            await browser_session.cdp_client.send.Browser.grantPermissions(params=params)
            logger.info(f"✅ Successfully granted permissions: {converted_permissions}")
            
        except Exception as e:
            logger.error(f"❌ Failed to grant permissions: {str(e)}")
            raise
    
    @staticmethod
    async def reset_permissions(browser_session, origin: Optional[str] = None):
        """
        Reset (revoke) permissions for a running browser session.
        
        Args:
            browser_session: The active browser session
            origin: Optional origin to reset permissions for
                   If None, permissions are reset for all origins.
        """
        logger.info(f"Resetting permissions" + (f" for {origin}" if origin else " for all origins"))
        
        try:
            params = {}
            if origin:
                params['origin'] = origin
                
            await browser_session.cdp_client.send.Browser.resetPermissions(params=params)
            logger.info(f"✅ Successfully reset permissions")
            
        except Exception as e:
            logger.error(f"❌ Failed to reset permissions: {str(e)}")
            raise
    
    @staticmethod
    def get_current_permissions(browser_session) -> List[str]:
        """
        Get currently granted permissions from the browser profile.
        
        Args:
            browser_session: The active browser session
            
        Returns:
            List of currently granted permissions
        """
        return browser_session.browser_profile.permissions
