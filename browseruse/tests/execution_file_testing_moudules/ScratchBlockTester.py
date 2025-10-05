import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import base64

# Add parent directories to path
_file_ = os.path.abspath(__file__)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), '../..')))

from tools.execution import Executor
from tools.filter import get_list_of_used_blocks
from dotenv import load_dotenv
import pychrome
from tools.browserUseClient import send_task

load_dotenv()

# PDF generation imports
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("⚠ WeasyPrint not available. Install with: pip install weasyprint")


class ScratchBlockTester:
    """
    Automated testing framework for Scratch block execution.
    Tests block placement and validates workspace state.
    """
    
    def __init__(self, debug_port=9222, tab_index=0):
        self.debug_port = debug_port
        self.executor = Executor(debug_port=debug_port, tab_index=tab_index)
        self.results_dir = Path("test_results")
        self.screenshots_dir = self.results_dir / "screenshots"
        self.results_dir.mkdir(exist_ok=True)
        self.screenshots_dir.mkdir(exist_ok=True)
        self.test_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.browser = pychrome.Browser(url=f"http://127.0.0.1:{self.debug_port}")
        self.tab = self.browser.list_tab()[tab_index]
        
    def create_test_dataset(self) -> List[Dict[str, Any]]:
        """
        Create a comprehensive test dataset with various block combinations.
        Returns a list of test cases with expected behaviors.
        """
        test_cases = [
        # {
        #     "test_id": "test_001",
        #     "description": "Basic event and control flow",
        #     "input": {
        #         "steps": [
        #             {"step": 1, "category": "Events", "block": "when green flag clicked"},
        #             {"step": 2, "category": "Control", "block": "forever"},
        #             {"step": 3, "category": "Looks", "block": "say message"}
        #         ]
        #     }
        # },
        # {
        #     "test_id": "test_002",
        #     "description": "Motion blocks sequence",
        #     "input": {
        #         "steps": [
        #             {"step": 1, "category": "Events", "block": "when green flag clicked"},
        #             {"step": 2, "category": "Motion", "block": "move steps"},
        #             {"step": 3, "category": "Motion", "block": "turn right"}
        #         ]
        #     }
        # },
        {
            "test_id": "test_003",
            "description": "Looks blocks with speech",
            "input": {
                "steps": [
                    {"step": 1, "category": "Events", "block": "when green flag clicked"},
                    {"step": 2, "category": "Looks", "block": "say message for seconds"},
                    {"step": 3, "category": "Looks", "block": "hide"},
                    {"step": 4, "category": "Looks", "block": "show"}
                ]
            }
        },
        {
            "test_id": "test_004",
            "description": "Control structures with repeat",
            "input": {
                "steps": [
                    {"step": 1, "category": "Events", "block": "when green flag clicked"},
                    {"step": 2, "category": "Control", "block": "repeat times"},
                    {"step": 3, "category": "Motion", "block": "move steps"}
                ]
            }
        },
        {
        "test_id": "test_005",
        "description": "Timer operations",
        "input": {
            "steps": [
                {"step": 1, "category": "Events", "block": "when green flag clicked"},
                {"step": 2, "category": "Sensing", "block": "reset timer"},
                {"step": 3, "category": "Control", "block": "repeat "},
                {"step": 4, "category": "Sound", "block": "start sound"},
                ]
            }
        },
        {
            "test_id": "test_006",
            "description": "Mouse following behavior",
            "input": {
                "steps": [
                    {"step": 1, "category": "Events", "block": "when green flag clicked"},
                    {"step": 2, "category": "Control", "block": "forever"},
                    {"step": 3, "category": "Motion", "block": "point towards"},
                    {"step": 4, "category": "Motion", "block": "move steps"}
                ]
            }
        },    
        {
            "test_id": "test_007",
            "description": "Complex animation loop",
            "input": {
                "steps": [
                    {"step": 1, "category": "Events", "block": "when green flag clicked"},
                    {"step": 2, "category": "Control", "block": "forever"},
                    {"step": 3, "category": "Motion", "block": "go to random position"},
                    {"step": 4, "category": "Looks", "block": "change graphic effect"},
                    {"step": 5, "category": "Control", "block": "wait seconds"}
                ]
            }
        },
        {
            "test_id": "test_008",
            "description": "Sprite positioning sequence",
            "input": {
                "steps": [
                    {"step": 1, "category": "Events", "block": "when green flag clicked"},
                    {"step": 2, "category": "Motion", "block": "go to position"},
                    {"step": 3, "category": "Motion", "block": "point in direction"},
                    {"step": 4, "category": "Motion", "block": "glide"}
                ]
            }
        },
        {
            "test_id": "test_009",
            "description": "Backdrop switching",
            "input": {
                "steps": [
                    {"step": 1, "category": "Events", "block": "when green flag clicked"},
                    {"step": 2, "category": "Looks", "block": "switch backdrop"},
                    {"step": 3, "category": "Control", "block": "wait seconds"},
                    {"step": 4, "category": "Looks", "block": "next backdrop"}
                ]
            }
        },
        {
            "test_id": "test_010",
            "description": "Edge detection and bounce",
            "input": {
                "steps": [
                    {"step": 1, "category": "Events", "block": "when green flag clicked"},
                    {"step": 2, "category": "Control", "block": "forever"},
                    {"step": 3, "category": "Motion", "block": "move steps"},
                    {"step": 4, "category": "Motion", "block": "if on edge bounce"}
                ]
            }
        }
    ]
        
        return test_cases
    
    def disable_beforeunload(self):
        """
        Disable the 'Changes that you made may not be saved' dialog
        by removing beforeunload event listeners.
        """
        try:
            self.tab.start()
            # Execute JavaScript to remove beforeunload handlers
            js_code = """
            window.onbeforeunload = null;
            window.addEventListener('beforeunload', function(e) {
                delete e['returnValue'];
            });
            """
            self.tab.call_method("Runtime.evaluate", expression=js_code, _timeout=5)
            print("✓ Disabled beforeunload confirmation dialog")
            self.tab.stop()
        except Exception as e:
            print(f"⚠ Warning: Could not disable beforeunload: {e}")
    
    def take_screenshot(self, test_id: str) -> str:
        """
        Capture a screenshot of the current workspace.
        
        Args:
            test_id: Test identifier for naming the screenshot
            
        Returns:
            Path to saved screenshot file
        """
        try:
            # Create a fresh connection for screenshot
            browser = pychrome.Browser(url=f"http://127.0.0.1:{self.debug_port}")
            tab = browser.list_tab()[0]
            tab.start()
            
            # Capture screenshot
            result = tab.call_method("Page.captureScreenshot", 
                                         format="png", 
                                         _timeout=10)
            
            # Decode and save screenshot
            screenshot_data = base64.b64decode(result['data'])
            screenshot_filename = f"{test_id}_{self.test_session_id}.png"
            screenshot_path = self.screenshots_dir / screenshot_filename
            
            with open(screenshot_path, 'wb') as f:
                f.write(screenshot_data)
            
            print(f"📸 Screenshot saved: {screenshot_filename}")
            tab.stop()
            
            return str(screenshot_path)
            
        except Exception as e:
            print(f"⚠ Error taking screenshot: {e}")
            return None
    
    def refresh_content(self):
        """
        Refresh content/DOM to get newly updated elements from the webpage.
        This does NOT reload the page - just updates the DOM state.
        """
        try:
            print("🔄 Refreshing content (send_task refresh)...")
            send_task("refresh")
            time.sleep(1.5)  # Wait for content to update
            print("✓ Content refreshed successfully")
        except Exception as e:
            print(f"⚠ Error refreshing content: {e}")
    
    def refresh_scratch_page(self):
        """
        Refresh the Scratch page to reset the workspace.
        """
        try:
            browser = pychrome.Browser(url=f"http://127.0.0.1:{self.debug_port}")
            tab = browser.list_tab()[0]
            tab.start()
            tab.call_method("Page.reload", _timeout=5)
            time.sleep(3)  # Wait for page to fully reload
            print("✓ Page refreshed successfully")
            tab.stop()
        except Exception as e:
            print(f"⚠ Error refreshing page: {e}")
    
    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single test case and capture results.
        
        Args:
            test_case: Dictionary containing test_id, description, and input
            
        Returns:
            Dictionary with test results including input, output, and metadata
        """
        test_id = test_case["test_id"]
        description = test_case["description"]
        input_data = test_case["input"]
        
        print(f"\n{'='*60}")
        print(f"Running {test_id}: {description}")
        print(f"{'='*60}")
        
        # Convert input to JSON string
        json_plan = json.dumps(input_data)
        
        # Record start time
        start_time = time.time()
        
        # Execute the plan
        execution_status = Executor.executor_tool(json_plan, delay=0.5)
        
        # Wait for blocks to settle
        time.sleep(2)
        
        # Refresh CONTENT (NOT page) to get updated DOM elements
        print("🔄 Refreshing content to get updated workspace state...")
        self.refresh_content()
        
        # Get the workspace state AFTER content refresh
        workspace_state = get_list_of_used_blocks()
        
        # Take screenshot of the result
        screenshot_path = self.take_screenshot(test_id)
        
        # Record end time
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Compile results
        result = {
            "test_id": test_id,
            "description": description,
            "input": input_data,
            "execution_status": execution_status,
            "workspace_state": workspace_state,
            "screenshot_path": screenshot_path,
            "execution_time_seconds": round(execution_time, 2),
            "timestamp": datetime.now().isoformat(),
            "steps_count": len(input_data["steps"])
        }
        
        print(f"\n✓ Test completed in {execution_time:.2f}s")
        print(f"Status: {execution_status}")
        print(f"\nWorkspace State:\n{workspace_state}")
        
        return result
    
    def run_all_tests(self, test_cases: List[Dict[str, Any]] = None, 
                      auto_refresh: bool = True) -> List[Dict[str, Any]]:
        """
        Run all test cases sequentially.
        
        Args:
            test_cases: List of test cases to run (uses default dataset if None)
            auto_refresh: Whether to refresh page between tests
            
        Returns:
            List of all test results
        """
        if test_cases is None:
            test_cases = self.create_test_dataset()
        
        all_results = []
        
        print(f"\n🚀 Starting test session: {self.test_session_id}")
        print(f"Total tests to run: {len(test_cases)}\n")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[Test {i}/{len(test_cases)}]")
            
            # Refresh page BEFORE each test to start with clean workspace
            if auto_refresh:
                print("\n🔄 Refreshing page before test...")
                self.refresh_scratch_page()
            
            # Run the test
            result = self.run_single_test(test_case)
            all_results.append(result)
            
            # Save individual test result
            self.save_individual_result(result)
        
        # Save consolidated results
        self.save_all_results(all_results)
        self.generate_summary_report(all_results)
        html_path = self.generate_html_report(all_results)
        
        # Generate PDF from HTML
        if WEASYPRINT_AVAILABLE:
            self.generate_pdf_report(html_path)
        else:
            print("\n⚠ PDF generation skipped (WeasyPrint not installed)")
        
        return all_results
    
    def save_individual_result(self, result: Dict[str, Any]):
        """Save individual test result to JSON file with workspace state."""
        filename = f"{result['test_id']}_{self.test_session_id}.json"
        filepath = self.results_dir / filename
        
        # Create a complete result object with all data
        complete_result = {
            "test_id": result['test_id'],
            "description": result['description'],
            "timestamp": result['timestamp'],
            "execution_time_seconds": result['execution_time_seconds'],
            "steps_count": result['steps_count'],
            "input_plan": result['input'],
            "execution_status": result['execution_status'],
            "workspace_state": result['workspace_state'],
            "screenshot_path": result.get('screenshot_path', 'N/A')
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(complete_result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved individual result with workspace state: {filename}")
    
    def save_all_results(self, results: List[Dict[str, Any]]):
        """Save all test results to a consolidated JSON file."""
        filename = f"all_tests_{self.test_session_id}.json"
        filepath = self.results_dir / filename
        
        consolidated = {
            "session_id": self.test_session_id,
            "total_tests": len(results),
            "test_results": results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(consolidated, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved consolidated results: {filename}")
    
    def generate_summary_report(self, results: List[Dict[str, Any]]):
        """Generate a human-readable summary report."""
        filename = f"summary_report_{self.test_session_id}.txt"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("SCRATCH BLOCK EXECUTION TEST REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"Session ID: {self.test_session_id}\n")
            f.write(f"Total Tests: {len(results)}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            total_time = sum(r['execution_time_seconds'] for r in results)
            f.write(f"Total Execution Time: {total_time:.2f} seconds\n")
            f.write(f"Average Time per Test: {total_time/len(results):.2f} seconds\n\n")
            
            f.write("="*70 + "\n")
            f.write("TEST RESULTS DETAIL\n")
            f.write("="*70 + "\n\n")
            
            for i, result in enumerate(results, 1):
                f.write(f"\n[Test {i}] {result['test_id']}\n")
                f.write("-"*70 + "\n")
                f.write(f"Description: {result['description']}\n")
                f.write(f"Steps Count: {result['steps_count']}\n")
                f.write(f"Execution Time: {result['execution_time_seconds']}s\n")
                f.write(f"Status: {result['execution_status']}\n")
                f.write(f"Screenshot: {result.get('screenshot_path', 'N/A')}\n\n")
                
                f.write("Input Steps:\n")
                for step in result['input']['steps']:
                    f.write(f"  {step['step']}. {step['category']} -> {step['block']}\n")
                
                f.write(f"\nWorkspace State:\n{result['workspace_state']}\n")
                f.write("\n" + "="*70 + "\n")
        
        print(f"📊 Generated summary report: {filename}")
    
    def generate_html_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate an HTML report with embedded screenshots.
        
        Returns:
            Path to the generated HTML file
        """
        filename = f"visual_report_{self.test_session_id}.html"
        filepath = self.results_dir / filename
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scratch Block Test Report - {self.test_session_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            background: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .test-case {{
            border: 1px solid #ddd;
            margin: 20px 0;
            padding: 20px;
            border-radius: 5px;
            background: #fafafa;
            page-break-inside: avoid;
        }}
        .test-header {{
            background: #2196F3;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            margin: -20px -20px 15px -20px;
        }}
        .test-steps {{
            background: white;
            padding: 10px;
            border-left: 3px solid #FF9800;
            margin: 10px 0;
        }}
        .screenshot {{
            max-width: 100%;
            border: 2px solid #ddd;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .workspace-state {{
            background: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            white-space: pre-wrap;
            font-size: 12px;
        }}
        .status {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
        }}
        .status-success {{
            background: #4CAF50;
            color: white;
        }}
        .metadata {{
            color: #666;
            font-size: 14px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Scratch Block Execution Test Report</h1>
        
        <div class="summary">
            <h2>Test Summary</h2>
            <p><strong>Session ID:</strong> {self.test_session_id}</p>
            <p><strong>Total Tests:</strong> {len(results)}</p>
            <p><strong>Total Execution Time:</strong> {sum(r['execution_time_seconds'] for r in results):.2f}s</p>
            <p><strong>Average Time per Test:</strong> {sum(r['execution_time_seconds'] for r in results)/len(results):.2f}s</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
"""
        
        for i, result in enumerate(results, 1):
            screenshot_rel_path = f"screenshots/{Path(result.get('screenshot_path', '')).name}" if result.get('screenshot_path') else ""
            
            html_content += f"""
        <div class="test-case">
            <div class="test-header">
                <h3>Test {i}: {result['test_id']}</h3>
            </div>
            
            <p><strong>Description:</strong> {result['description']}</p>
            
            <div class="metadata">
                <span class="status status-success">{result['execution_status']}</span>
                <span>⏱️ {result['execution_time_seconds']}s</span>
                <span>📦 {result['steps_count']} steps</span>
            </div>
            
            <div class="test-steps">
                <h4>📝 Input Steps:</h4>
                <ol>
"""
            
            for step in result['input']['steps']:
                html_content += f"                    <li><strong>{step['category']}</strong> → {step['block']}</li>\n"
            
            html_content += f"""
                </ol>
            </div>
            
            <h4>📸 Visual Result:</h4>
            <img src="{screenshot_rel_path}" alt="Test {result['test_id']} Screenshot" class="screenshot">
            
            <h4>📊 Workspace State:</h4>
            <div class="workspace-state">{result['workspace_state']}</div>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"🌐 Generated HTML report: {filename}")
        return str(filepath)
    
    def generate_pdf_report(self, html_path: str):
        """
        Generate a PDF report from the HTML file.
        
        Args:
            html_path: Path to the HTML file to convert
        """
        try:
            pdf_filename = f"visual_report_{self.test_session_id}.pdf"
            pdf_path = self.results_dir / pdf_filename
            
            print(f"📄 Generating PDF report...")
            
            # Convert HTML to PDF
            HTML(html_path).write_pdf(pdf_path)
            
            print(f"✅ PDF report generated: {pdf_filename}")
            
        except Exception as e:
            print(f"⚠ Error generating PDF: {e}")
            print("Tip: Make sure WeasyPrint and its dependencies are installed correctly")


def main():
    """
    Main function to run the test suite.
    """
    print("🎯 Scratch Block Testing Framework")
    print("="*60)
    
    # Initialize tester
    tester = ScratchBlockTester(debug_port=9222, tab_index=0)
    
    # Run default test dataset
    print("\nRunning default test dataset...")
    results = tester.run_all_tests(auto_refresh=True)
    
    print("\n" + "="*60)
    print("✅ Testing completed!")
    print(f"📁 Results saved in: {tester.results_dir}")
    print(f"📸 Screenshots saved in: {tester.screenshots_dir}")
    print(f"🌐 HTML Report: visual_report_{tester.test_session_id}.html")
    if WEASYPRINT_AVAILABLE:
        print(f"📄 PDF Report: visual_report_{tester.test_session_id}.pdf")
    print("="*60)


if __name__ == "__main__":
    main()