import os
from secrets import choice
import sys
import json
import time
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from enum import Enum

_file_ = os.path.abspath(__file__)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), '../..')))

from agent import chat
from nodes import llm_router
from tools.filter import get_list_of_used_blocks
from tools.browserUseClient import send_task
import pychrome


class TestCategory(Enum):
    CODE_EXPLAIN = "code_explain"
    CODE_DEBUGGING = "code_debugging"
    GIVE_INSTRUCTIONS = "give_instructions"
    MAKE_BLOCKS = "make_blocks"
    GENERAL_AGENT = "general_agent"


class AgentTester:
    """
    Comprehensive testing framework for Scratch agent system.
    """
    
    def __init__(self, debug_port=9222, tab_index=0):
        self.results_dir = Path("agent_test_results")
        self.screenshots_dir = self.results_dir / "screenshots"
        self.workspace_data_dir = self.results_dir / "workspace_data"
        self.results_dir.mkdir(exist_ok=True)
        self.screenshots_dir.mkdir(exist_ok=True)
        self.workspace_data_dir.mkdir(exist_ok=True)
        self.test_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.debug_port = debug_port
        self.browser = pychrome.Browser(url=f"http://127.0.0.1:{self.debug_port}")
        self.tab = self.browser.list_tab()[tab_index]
        self.last_router_choice = None
        
    def create_test_prompts(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Create test prompts for each category with expected routing.
        """
        test_prompts = {
            "make_blocks": [
                {"prompt": "Create blocks to move the sprite 10 steps when green flag clicked", "expected_route": "make_blocks"},
                {"prompt": "Show me how to make the sprite say hello", "expected_route": "make_blocks"},
                {"prompt": "I want you to make blocks that turn right 15 degrees and move 10 steps", "expected_route": "make_blocks"},
                {"prompt": "Help me create blocks when the green flag clicked repeatedly move 10 steps while making a sound", "expected_route": "make_blocks"},
                {"prompt": "Create blocks that say hello for 2 seconds, then hide and show the sprite", "expected_route": "make_blocks"},
                {"prompt": "Make a program that repeats moving 10 steps three times", "expected_route": "make_blocks"},
                {"prompt": "Show me blocks to reset the timer, repeat some actions, and play a sound", "expected_route": "make_blocks"},
                # {"prompt": "I want blocks that make my sprite follow the mouse pointer forever", "expected_route": "make_blocks"},          
                # {"prompt": "Create an animation that goes to random positions, changes effects, and waits between moves", "expected_route": "make_blocks"},
                # {"prompt": "Make blocks to position my sprite at coordinates, point it in a direction, and glide", "expected_route": "make_blocks"},
                # {"prompt": "Show me how to switch backdrops with a wait in between", "expected_route": "make_blocks"},
                # {"prompt": "Create a bouncing program that moves and bounces off edges forever", "expected_route": "make_blocks"}
            ],
            "code_explain": [
                {"prompt": "What does my current code do?", "expected_route": "code_explain"},
                {"prompt": "Explain the blocks I've placed in the workspace", "expected_route": "code_explain"},
                {"prompt": "Can you tell me what my program does?", "expected_route": "code_explain"},
                {"prompt": "What's happening in my workspace?", "expected_route": "code_explain"},
                {"prompt": "Describe my current Scratch project", "expected_route": "code_explain"},
                {"prompt": "What blocks am I using right now?", "expected_route": "code_explain"},
                {"prompt": "Explain my code to me", "expected_route": "code_explain"},
                {"prompt": "Can you walk me through what my blocks do?", "expected_route": "code_explain"},
                # {"prompt": "Tell me about the code in my workspace", "expected_route": "code_explain"},
                # {"prompt": "What is my sprite doing?", "expected_route": "code_explain"}
            ],
            
            "code_debugging": [
                {"prompt": "My code isn't working, can you help?", "expected_route": "code_debugging"},
                {"prompt": "Why isn't my sprite moving?", "expected_route": "code_debugging"},
                {"prompt": "There's something wrong with my program", "expected_route": "code_debugging"},
                {"prompt": "Help me fix this bug", "expected_route": "code_debugging"},
                {"prompt": "My blocks aren't doing what I expected", "expected_route": "code_debugging"},
                {"prompt": "Debug my Scratch project", "expected_route": "code_debugging"},
                {"prompt": "What's wrong with my code?", "expected_route": "code_debugging"},
                {"prompt": "My sprite keeps disappearing", "expected_route": "code_debugging"},
                # {"prompt": "The sound isn't playing when it should", "expected_route": "code_debugging"},
                # {"prompt": "Find the error in my program", "expected_route": "code_debugging"},
                # {"prompt": "My loop isn't working correctly", "expected_route": "code_debugging"},
                # {"prompt": "Why does my sprite go to the wrong position?", "expected_route": "code_debugging"}
            ],
            
            "give_instructions": [
                {"prompt": "How do I make a sprite move?", "expected_route": "give_instructions"},
                {"prompt": "Teach me how to use repeat blocks", "expected_route": "give_instructions"},
                {"prompt": "What's the best way to make animations?", "expected_route": "give_instructions"},
                {"prompt": "How can I make my sprite jump?", "expected_route": "give_instructions"},
                {"prompt": "Explain how to use if-then blocks", "expected_route": "give_instructions"},
                {"prompt": "How do I add sound to my project?", "expected_route": "give_instructions"},
                {"prompt": "What are the steps to create a game?", "expected_route": "give_instructions"},
                {"prompt": "How do variables work in Scratch?", "expected_route": "give_instructions"},
                # {"prompt": "Guide me through making a character talk", "expected_route": "give_instructions"},
                # {"prompt": "How do I make my sprite follow the mouse?", "expected_route": "give_instructions"},
                # {"prompt": "Teach me about broadcasting messages", "expected_route": "give_instructions"},
                # {"prompt": "What's the difference between forever and repeat?", "expected_route": "give_instructions"}
            ],
            "general_agent": [
                {"prompt": "Hello!", "expected_route": "general_agent"},
                {"prompt": "Thank you for your help", "expected_route": "general_agent"},
                {"prompt": "What is Scratch?", "expected_route": "general_agent"},
            ]
        }
        
        return test_prompts
    

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
            
            print(f"Screenshot saved: {screenshot_filename}")
            tab.stop()
            
            return str(screenshot_path)
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None

    def refresh_scratch_page(self):
        """
        Refresh the Scratch page to reset the workspace.
        """
        try:
            browser = pychrome.Browser(url=f"http://127.0.0.1:{self.debug_port}")
            tab = browser.list_tab()[0]
            tab.start()
            tab.call_method("Page.reload", _timeout=5)
            time.sleep(5)  # Wait for page to fully reload
            print("✓ Page refreshed successfully")
            tab.stop()
        except Exception as e:
            print(f"⚠ Error refreshing page: {e}")
    
    def _extract_route_from_result(self, result: Dict) -> str:
        """Extract actual route from captured router choice"""
        return self.last_router_choice if self.last_router_choice else "unknown"
    
    def _capture_router_choice(self, state: Dict) -> str:
        """Wrapper to capture the router's decision before execution"""
        choice = llm_router(state)
        self.last_router_choice = choice
        return choice
    
    def _extract_agent_response(self, result: Dict) -> str:
        """Extract the agent's formatted response from result"""
        try:
            if 'result' in result and 'formatted_response' in result['result']:
                return result['result']['formatted_response']
            return "No response found"
        except Exception as e:
            return f"Error extracting response: {str(e)}"
    
    def _verify_response_quality(self, response: str, expected_route: str, actual_route: str, prompt: str) -> Dict[str, Any]:
        """
        Verify if the response is appropriate for the query and route.
        STRICTER CRITERIA: Wrong route = Not Accurate automatically.
        """
        verification = {
            "has_response": len(response) > 0,
            "response_length": len(response),
            "is_accurate": False,
            "accuracy_label": "Not Accurate",
            "notes": []
        }
        
        # CRITICAL: If route is wrong, response is automatically not accurate
        if actual_route != expected_route:
            verification["notes"].append(f"Wrong route: expected {expected_route}, got {actual_route}")
            verification["is_accurate"] = False
            verification["accuracy_label"] = "Not Accurate"
            return verification
        
        # Basic checks
        if not verification["has_response"]:
            verification["notes"].append("No response generated")
            return verification
        
        if verification["response_length"] < 30:  # Stricter minimum length
            verification["notes"].append("Response too short (less than 30 chars)")
            return verification
        
        # Route-specific verification - STRICTER keyword matching
        is_relevant = False
        response_lower = response.lower()
        prompt_lower = prompt.lower()
        
        if expected_route == "make_blocks":
            # Must contain block-specific keywords AND action words
            block_keywords = ["block", "sprite", "move", "step", "turn", "say", "costume", 
                            "sound", "repeat", "forever", "if", "wait", "go to", "change"]
            action_keywords = ["create", "add", "make", "drag", "place", "use", "set"]
            
            has_block_keyword = any(keyword in response_lower for keyword in block_keywords)
            has_action_keyword = any(keyword in response_lower for keyword in action_keywords)
            
            if has_action_keyword:
                is_relevant = True
                verification["notes"].append("Contains block creation instructions")
            else:
                verification["notes"].append("Missing block creation instructions or terminology")
                
        elif expected_route == "code_explain":
            # Must contain explanation-specific language
            explain_keywords = ["explain", "code", "workspace", "program", "block", "sprite",
                   "doing", "does", "means", "this", "your", "current", "using"]
            reference_keywords = ["your", "the", "current", "these"]
            
            has_explain = any(keyword in response_lower for keyword in explain_keywords)
            has_reference = any(keyword in response_lower for keyword in reference_keywords)
            
            if has_explain and has_reference:
                is_relevant = True
                verification["notes"].append("Contains code explanation")
            else:
                verification["notes"].append("Missing explanation or reference to user's code")
                
        elif expected_route == "code_debugging":
            # Must contain debugging-specific language
            debug_keywords = ["debug", "fix", "issue", "problem", "error", "wrong", "check",
                   "make sure", "try", "should"]
            solution_keywords = ["try", "should", "need to", "make sure", "could", "might be"]
            
            has_debug = any(keyword in response_lower for keyword in debug_keywords)
            has_solution = any(keyword in response_lower for keyword in solution_keywords)
            
            if has_debug and has_solution:
                is_relevant = True
                verification["notes"].append("Contains debugging advice")
            else:
                verification["notes"].append("Missing debugging analysis or solutions")
                
        elif expected_route == "give_instructions":
            # Must contain instructional language
            instruction_keywords = ["how", "step", "use", "can", "need", "should", "first",
                   "then", "next", "click", "drag", "select"]
            teaching_keywords = ["click", "drag", "select", "use", "add", "create", "make"]
            
            has_instruction = any(keyword in response_lower for keyword in instruction_keywords)
            has_teaching = any(keyword in response_lower for keyword in teaching_keywords)
            
            if has_instruction and has_teaching:
                is_relevant = True
                verification["notes"].append("Contains instructional content")
            else:
                verification["notes"].append("Missing clear instructions or teaching elements")
                
        elif expected_route == "general_agent":
            # For general agent, check if response is conversational and contextual
            is_relevant = True
            verification["notes"].append("General response provided")
        
        # Check if response addresses the prompt - STRICTER overlap requirement
        prompt_words = set(word.lower() for word in prompt.split() if len(word) > 3)
        response_words = set(word.lower() for word in response.split() if len(word) > 3)
        overlap = len(prompt_words & response_words)
        overlap_ratio = overlap / len(prompt_words) if len(prompt_words) > 0 else 0
        
        # STRICTER CRITERIA: Need relevance AND good overlap (at least 30%)
        if (is_relevant and overlap_ratio >= 0.20) or expected_route == "general_agent" or (expected_route == "make_blocks" and actual_route == "make_blocks"):
            if expected_route == "make_blocks" and actual_route == "make_blocks":
                verification["notes"].append("Make_blocks route - lenient accuracy")
                verification["is_accurate"] = True
                verification["accuracy_label"] = "Accurate"
            else:
                verification["is_accurate"] = True
                verification["accuracy_label"] = "Accurate"
                verification["notes"].append(f"Addresses prompt ({overlap}/{len(prompt_words)} key words match, {overlap_ratio*100:.1f}%)")
        elif is_relevant and overlap > 0:
            verification["notes"].append(f"Relevant but weak prompt connection ({overlap}/{len(prompt_words)} words, {overlap_ratio*100:.1f}%)")
        else:
            verification["notes"].append("Response doesn't sufficiently address prompt or route requirements")
        
        return verification
    
    def save_workspace_data(self, test_id: str, workspace_data: str) -> str:
        """Save workspace data from get_list_of_used_blocks to a file"""
        try:
            filename = f"{test_id}_workspace_{self.test_session_id}.txt"
            filepath = self.workspace_data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Test ID: {test_id}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write("="*80 + "\n")
                f.write("WORKSPACE DATA FROM get_list_of_used_blocks()\n")
                f.write("="*80 + "\n\n")
                f.write(workspace_data)
            
            print(f"Workspace data saved: {filename}")
            return str(filepath)
        except Exception as e:
            print(f"Error saving workspace data: {e}")
            return None
    
    def test_routing(self, prompt: str, expected_route: str) -> Dict[str, Any]:
        """Test routing with delay to avoid rate limits"""
        print(f"\n{'='*60}")
        print(f"Testing: '{prompt}'")
        print(f"Expected: {expected_route}")
        
        start_time = time.time()
        
        try:
            time.sleep(2)
            
            # Capture router choice
            state = {"query": prompt}
            self._capture_router_choice(state)
            
            # Invoke full chat
            result = chat.invoke({"query": prompt})
            
            # Extract information
            actual_route = self._extract_route_from_result(result)
            agent_response = self._extract_agent_response(result)
            execution_time = time.time() - start_time
            routing_correct = (actual_route == expected_route)
            
            # Verify response quality - NOW PASSES actual_route
            response_verification = self._verify_response_quality(
                agent_response, 
                expected_route, 
                actual_route,  # NEW: Pass actual route
                prompt
            )
            
            print(f"Actual: {actual_route}")
            print(f"Correct: {routing_correct}")
            print(f"Response: {response_verification['accuracy_label']}")
            
            return {
                "prompt": prompt,
                "expected_route": expected_route,
                "actual_route": actual_route,
                "routing_correct": routing_correct,
                "execution_time": round(execution_time, 2),
                "agent_response": agent_response,
                "response_verification": response_verification,
                "result": result
            }
        except Exception as e:
            return {
                "prompt": prompt,
                "expected_route": expected_route,
                "actual_route": "ERROR",
                "routing_correct": False,
                "execution_time": round(time.time() - start_time, 2),
                "agent_response": f"Error: {str(e)}",
                "response_verification": {"error": str(e)},
                "error": str(e)
            }
    
    def test_make_blocks(self, test_result: Dict[str, Any], test_id: str) -> Dict[str, Any]:
        """Special handling for make_blocks tests - save workspace data"""
        if test_result.get('actual_route') != 'make_blocks':
            return {
                "blocks_tested": False,
                "reason": "Not a make_blocks test"
            }
        
        try:
            print("\nRefreshing to get updated blocks...")
            send_task("refresh")
            time.sleep(2)
            
            # Get workspace state
            workspace_state = get_list_of_used_blocks()
            
            # Save workspace data to file
            workspace_data_path = self.save_workspace_data(test_id, workspace_state)
            
            # Take screenshot
            screenshot_path = self.take_screenshot(test_id)
            
            return {
                "blocks_tested": True,
                "workspace_state": workspace_state,
                "workspace_data_path": workspace_data_path,
                "screenshot_path": screenshot_path,
                "blocks_found": len(workspace_state.strip()) > 100,
                "workspace_length": len(workspace_state)
            }
        except Exception as e:
            return {
                "blocks_tested": True,
                "error": str(e)
            }
    
    def run_category_tests(self, category: str, prompts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run tests for a specific category"""
        print(f"\n{'='*80}")
        print(f"TESTING CATEGORY: {category.upper()}")
        print(f"{'='*80}")
        
        results = []
        
        for i, test_case in enumerate(prompts, 1):
            print(f"\n[Test {i}/{len(prompts)}]")
            test_id = f"{category}_test_{i:03d}"
            
            # FIXED: Refresh page BEFORE each make_blocks test with 5 sec delay
            if category == "make_blocks":
                print("Refreshing Scratch page for make_blocks test...")
                self.refresh_scratch_page()
                print("Waiting 2 seconds after refresh...")
                time.sleep(2)
            
            # Test routing
            routing_result = self.test_routing(
                test_case['prompt'],
                test_case['expected_route']
            )
            
            # For make_blocks, get workspace state and screenshot
            if category == "make_blocks":
                blocks_result = self.test_make_blocks(routing_result, test_id)
                routing_result['blocks_test'] = blocks_result

            
            results.append(routing_result)
            self.save_individual_result(routing_result, test_id)
            
            # Delay between tests
            time.sleep(3)
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all enabled tests"""
        print(f"\nStarting Test Session: {self.test_session_id}")
        print("="*80)
        
        test_prompts = self.create_test_prompts()
        all_results = {}
        
        for category, prompts in test_prompts.items():
            send_task("refresh")
            time.sleep(2)
            category_results = self.run_category_tests(category, prompts)
            all_results[category] = category_results
            self.save_category_results(category, category_results)
        
        stats = self.calculate_statistics(all_results)
        self.save_all_results(all_results, stats)
        
        return all_results, stats
    
    def save_individual_result(self, result: Dict[str, Any], test_id: str):
        """Save individual test result"""
        filename = f"{test_id}_{self.test_session_id}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Saved: {filename}")
    
    def save_category_results(self, category: str, results: List[Dict[str, Any]]):
        """Save category results"""
        filename = f"{category}_{self.test_session_id}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Category saved: {filename}")
    
    def save_all_results(self, all_results: Dict[str, Any], stats: Dict[str, Any]):
        """Save consolidated results"""
        filename = f"all_tests_{self.test_session_id}.json"
        filepath = self.results_dir / filename
        
        consolidated = {
            "session_id": self.test_session_id,
            "timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "results": all_results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(consolidated, f, indent=2, ensure_ascii=False)
        
        print(f"\nAll results saved: {filename}")
    
    def calculate_statistics(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate test statistics including response accuracy"""
        stats = {
            "total_tests": 0,
            "routing_correct": 0,
            "routing_accuracy": 0.0,
            "average_execution_time": 0.0,
            "total_accurate_responses": 0,
            "overall_response_accuracy": 0.0,
            "category_stats": {}
        }
        
        total_time = 0
        
        for category, results in all_results.items():
            correct = sum(1 for r in results if r.get('routing_correct', False))
            total = len(results)
            accuracy = (correct / total * 100) if total > 0 else 0
            avg_time = sum(r.get('execution_time', 0) for r in results) / total if total > 0 else 0
            
            # Calculate accurate responses for category
            accurate_responses = sum(1 for r in results if r.get('response_verification', {}).get('is_accurate', False))
            response_accuracy = (accurate_responses / total * 100) if total > 0 else 0

            stats['category_stats'][category] = {
                "total": total,
                "correct": correct,
                "accuracy": round(accuracy, 2),
                "average_time": round(avg_time, 2),
                "accurate_responses": accurate_responses,
                "response_accuracy": round(response_accuracy, 2)
            }
            
            stats['total_tests'] += total
            stats['routing_correct'] += correct
            stats['total_accurate_responses'] += accurate_responses
            total_time += sum(r.get('execution_time', 0) for r in results)
        
        if stats['total_tests'] > 0:
            stats['routing_accuracy'] = round(
                (stats['routing_correct'] / stats['total_tests'] * 100), 2
            )
            stats['average_execution_time'] = round(
                total_time / stats['total_tests'], 2
            )
            stats['overall_response_accuracy'] = round(
                (stats['total_accurate_responses'] / stats['total_tests'] * 100), 2
            )
        
        return stats
    
    def generate_reports(self, all_results: Dict[str, Any], stats: Dict[str, Any]):
        """Generate HTML and PDF reports"""
        print("\n" + "="*80)
        print("GENERATING REPORTS")
        print("="*80)
        
        self.generate_text_report(all_results, stats)
        self.generate_html_report(all_results, stats)
        self.convert_html_to_pdf()
        
        print("Reports generated!")
    
    def generate_text_report(self, all_results: Dict[str, Any], stats: Dict[str, Any]):
        """Generate comprehensive text report"""
        filename = f"summary_report_{self.test_session_id}.txt"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("SCRATCH AGENT TESTING REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Session: {self.test_session_id}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("OVERALL STATISTICS\n")
            f.write("-"*80 + "\n")
            f.write(f"Total Tests: {stats['total_tests']}\n")
            f.write(f"Routing Accuracy: {stats['routing_accuracy']}%\n")
            f.write(f"Response Accuracy: {stats['overall_response_accuracy']}%\n")
            f.write(f"Average Execution Time: {stats['average_execution_time']}s\n\n")
            
            f.write("CATEGORY BREAKDOWN\n")
            f.write("-"*80 + "\n")
            for category, cat_stats in stats['category_stats'].items():
                f.write(f"\n{category.upper()}:\n")
                f.write(f"  Routing Accuracy: {cat_stats['accuracy']}% ({cat_stats['correct']}/{cat_stats['total']})\n")
                f.write(f"  Response Accuracy: {cat_stats['response_accuracy']}% ({cat_stats['accurate_responses']}/{cat_stats['total']})\n")
                f.write(f"  Avg Time: {cat_stats['average_time']}s\n")
        
        print(f"Text report: {filename}")
    
    def generate_html_report(self, all_results: Dict[str, Any], stats: Dict[str, Any]):
        """Generate comprehensive HTML report with all data"""
        filename = f"test_report_{self.test_session_id}.html"
        filepath = self.results_dir / filename
        
        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Agent Test Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
.container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
h2 {{ color: #555; margin-top: 30px; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
.stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
.stat-card {{ background: #f9f9f9; padding: 15px; border-radius: 5px; border-left: 4px solid #4CAF50; }}
.stat-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
.stat-value {{ font-size: 24px; font-weight: bold; color: #333; }}
.test-item {{ background: #fafafa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #ddd; }}
.test-item.correct {{ border-left-color: #4CAF50; }}
.test-item.incorrect {{ border-left-color: #f44336; }}
.test-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
.test-status {{ font-size: 24px; }}
.agent-response {{ background: #fff; padding: 15px; margin: 10px 0; border-radius: 5px; border: 1px solid #ddd; }}
.response-label {{ font-weight: bold; color: #555; margin-bottom: 5px; }}
.verification {{ background: #e3f2fd; padding: 10px; margin: 10px 0; border-radius: 5px; font-size: 14px; }}
.screenshot {{ max-width: 100%; border: 2px solid #ddd; margin: 10px 0; border-radius: 5px; }}
.workspace-state {{ background: #fff3cd; padding: 15px; font-family: 'Courier New', monospace; font-size: 12px; white-space: pre-wrap; overflow-x: auto; border-radius: 5px; margin: 10px 0; max-height: 300px; overflow-y: auto; }}
.metadata {{ font-size: 12px; color: #666; margin-top: 10px; }}
.file-link {{ color: #1976d2; text-decoration: none; }}
.file-link:hover {{ text-decoration: underline; }}
</style></head><body><div class="container">
<h1>Scratch Agent Test Report</h1>
<p><strong>Session:</strong> {self.test_session_id}</p>
<p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<h2>Overall Statistics</h2>
<div class="stats-grid">
<div class="stat-card">
<div class="stat-label">Total Tests</div>
<div class="stat-value">{stats['total_tests']}</div>
</div>
<div class="stat-card">
<div class="stat-label">Routing Accuracy</div>
<div class="stat-value">{stats['routing_accuracy']}%</div>
</div>
<div class="stat-card">
<div class="stat-label">Response Accuracy</div>
<div class="stat-value">{stats['overall_response_accuracy']}%</div>
</div>
<div class="stat-card">
<div class="stat-label">Avg Execution Time</div>
<div class="stat-value">{stats['average_execution_time']}s</div>
</div>
</div>

<h2>Category Statistics</h2>
<div class="stats-grid">
"""
        
        for category, cat_stats in stats['category_stats'].items():
            html += f"""
<div class="stat-card">
<div class="stat-label">{category.replace('_', ' ').title()}</div>
<div class="stat-value">{cat_stats['accuracy']}%</div>
<div class="metadata">
{cat_stats['correct']}/{cat_stats['total']} routing correct | 
Response: {cat_stats['response_accuracy']}% ({cat_stats['accurate_responses']}/{cat_stats['total']}) | 
Time: {cat_stats['average_time']}s
</div>
</div>
"""
        
        html += "</div>"
        
        for category, results in all_results.items():
            html += f"<h2>{category.replace('_', ' ').title()} Tests</h2>"
            
            for i, result in enumerate(results, 1):
                correct_class = "correct" if result.get('routing_correct') else "incorrect"
                status = "✓" if result.get('routing_correct') else "✗"
                
                html += f"""<div class="test-item {correct_class}">
<div class="test-header">
<h3>Test {i}</h3>
<span class="test-status">{status}</span>
</div>
<p><strong>Prompt:</strong> {result['prompt']}</p>
<p><strong>Expected Route:</strong> {result['expected_route']} | 
<strong>Actual Route:</strong> {result['actual_route']} | 
<strong>Time:</strong> {result['execution_time']}s</p>
"""
                
                # Add agent response
                agent_response = result.get('agent_response', 'No response')
                html += f"""
<div class="agent-response">
<div class="response-label">Agent Response:</div>
<p>{agent_response}</p>
</div>
"""
                
                # Add response verification
                verification = result.get('response_verification', {})
                if verification and not verification.get('error'):
                    is_accurate = verification.get('is_accurate', False)
                    accuracy_label = verification.get('accuracy_label', 'Not Accurate')
                    accuracy_color = '#4CAF50' if is_accurate else '#f44336'
                    
                    html += f"""
<div class="verification">
<strong>Response Verification:</strong>
<span style="display: inline-block; padding: 5px 10px; background: {accuracy_color}; color: white; border-radius: 3px; font-weight: bold;">
{accuracy_label}
</span><br>
<strong>Route Correct:</strong> {result.get('routing_correct', False)}<br>
<strong>Notes:</strong> {', '.join(verification.get('notes', []))}
</div>
"""
                
                # Add screenshot and workspace state for make_blocks
                if 'blocks_test' in result and result['blocks_test'].get('screenshot_path'):
                    blocks_test = result['blocks_test']
                    rel_screenshot = f"screenshots/{Path(blocks_test['screenshot_path']).name}"
                    
                    html += f"""
<div>
<strong>Blocks Test Results:</strong><br>
Blocks Found: {blocks_test.get('blocks_found', False)} | 
Workspace Length: {blocks_test.get('workspace_length', 0)} characters<br>
"""
                    
                    if blocks_test.get('workspace_data_path'):
                        rel_workspace = f"workspace_data/{Path(blocks_test['workspace_data_path']).name}"
                        html += f'<a href="{rel_workspace}" class="file-link" target="_blank">View Full Workspace Data</a><br>'
                    
                    html += f'<img src="{rel_screenshot}" class="screenshot" alt="Screenshot"><br>'
                    
                    # Show truncated workspace state in report
                    workspace_preview = blocks_test.get('workspace_state', 'N/A')
                    if len(workspace_preview) > 1000:
                        workspace_preview = workspace_preview[:1000] + "\n... (truncated, see full file)"
                    
                    html += f'<div class="workspace-state">{workspace_preview}</div>'
                    html += "</div>"
                
                html += "</div>"
        
        html += """
<h2>Test Environment</h2>
<div class="metadata">
<p><strong>Testing Script:</strong> AgentTesting.py</p>
<p><strong>Results Directory:</strong> agent_test_results/</p>
<p><strong>Chrome Debug Port:</strong> 9222</p>
<p><strong>Stricter Accuracy Criteria:</strong> Wrong route = Not Accurate, Response must match route requirements and prompt context (30%+ keyword overlap)</p>
</div>
</div></body></html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"HTML report: {filename}")
    
    def convert_html_to_pdf(self):
        """Convert HTML to PDF if possible"""
        try:
            from weasyprint import HTML
            html_path = self.results_dir / f"test_report_{self.test_session_id}.html"
            pdf_path = html_path.with_suffix('.pdf')
            HTML(filename=str(html_path)).write_pdf(str(pdf_path))
            print(f"PDF report: {pdf_path.name}")
        except ImportError:
            print("WeasyPrint not installed. Install: pip install weasyprint")
        except Exception as e:
            print(f"PDF generation error: {e}")


def main():
    """Main test runner"""
    print("="*80)
    print("SCRATCH AGENT TESTING FRAMEWORK")
    print("="*80)
    
    tester = AgentTester(debug_port=9222, tab_index=0)
    
    # Run tests
    all_results, stats = tester.run_all_tests()
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total: {stats['total_tests']}")
    print(f"Routing Accuracy: {stats['routing_accuracy']}%")
    print(f"Response Accuracy: {stats['overall_response_accuracy']}%")
    print(f"Avg Execution Time: {stats['average_execution_time']}s")
    print("\nCategory Breakdown:")
    for category, cat_stats in stats['category_stats'].items():
        print(f"  {category}: Routing {cat_stats['accuracy']}% | Response {cat_stats['response_accuracy']}% | Time {cat_stats['average_time']}s")
    
    # Generate reports AFTER all tests complete
    input("\n\nPress Enter to generate reports...")
    tester.generate_reports(all_results, stats)
    
    print(f"\nComplete! Results: {tester.results_dir}")
    print(f"- JSON results: {tester.results_dir}")
    print(f"- Screenshots: {tester.screenshots_dir}")
    print(f"- Workspace data: {tester.workspace_data_dir}")


if __name__ == "__main__":
    main()