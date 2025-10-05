import os
import time
import subprocess
import sys
from pathlib import Path
import datetime

# Configuration
EXTENSION_PATH = os.path.abspath("E:\\VS CODE\\Agentic AI\\BrowserUse\\avatar_ext")
TEST_URL = "https://scratch.mit.edu/projects/editor/"

# Define all test cases
TEST_CASES = [
    {
        "name": "Basic Short Phrase",
        "phrase": "Hello world",
        "purpose": "Baseline accuracy with simple, common words"
    },
    {
        "name": "Numbers and Counting",
        "phrase": "1 2 3 4 5 6 7 9 8 10",
        "purpose": "Recognition of numbers with similar phonetic patterns"
    },
    {
        "name": "Technical Terminology",
        "phrase": "Python programming uses variables functions and loops",
        "purpose": "Accuracy with technical/programming terminology"
    },
    {
        "name": "Proper Nouns",
        "phrase": "Google Microsoft Amazon and Apple are technology companies",
        "purpose": "Recognition of brand names and proper nouns"
    },
    {
        "name": "Question Format",
        "phrase": "What time is the meeting scheduled for tomorrow afternoon",
        "purpose": "Question phrasing and interrogative structure"
    },
    {
        "name": "Homophones",
        "phrase": "Their new car is parked over there by their house",
        "purpose": "Difficult homophones that sound alike but are spelled differently"
    },
    {
        "name": "Complex Sentence",
        "phrase": "The quick brown fox jumped over the lazy dog while it was sleeping",
        "purpose": "Classic pangram with varied phonetics and longer structure"
    },
    {
        "name": "Special Characters & Punctuation",
        "phrase": "Email me at john dot doe at example dot com with your results",
        "purpose": "Recognition of spoken special characters and email formatting"
    },
    {
        "name": "Command Phrase",
        "phrase": "Open the browser and navigate to the homepage then click login",
        "purpose": "Command sequences for virtual assistant contexts"
    },
    {
        "name": "Fast Speech Test",
        "phrase": "Supercalifragilisticexpialidocious is extraordinarily difficult to pronounce correctly",
        "purpose": "Fast speech and challenging vocabulary"
    }
]

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def launch_chrome_with_extension():
    """Launch Chrome with the extension loaded."""
    try:
        # Determine Chrome path based on OS
        chrome_path = None
        if os.name == 'nt':  # Windows
            paths_to_try = [
                os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Google\\Chrome\\Application\\chrome.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Google\\Chrome\\Application\\chrome.exe'),
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            for path in paths_to_try:
                if os.path.exists(path):
                    chrome_path = path
                    break
        
        if not chrome_path:
            print("❌ Could not locate Chrome. Please specify the path manually.")
            return False
            
        # Create user data directory for testing
        user_data_dir = os.path.abspath("manual-test-profile")
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Launch Chrome with arguments
        cmd = [
            chrome_path,
            f"--load-extension={EXTENSION_PATH}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--auto-open-devtools-for-tabs",
            TEST_URL
        ]
        
        print(f"\n🚀 Launching Chrome with extension from: {EXTENSION_PATH}")
        subprocess.Popen(cmd)
        return True
        
    except Exception as e:
        print(f"❌ Error launching Chrome: {e}")
        return False

def calculate_accuracy(expected, recognized):
    """Calculate word-level accuracy between expected and recognized text."""
    if not recognized:
        return 0.0
    
    expected_words = expected.lower().split()
    recognized_words = recognized.lower().split()
    
    # Count matching words
    matches = sum(1 for w in recognized_words if w in expected_words)
    total_expected = len(expected_words)
    
    return (matches / total_expected * 100) if total_expected > 0 else 0

def run_test_suite():
    """Run all test cases and generate a comprehensive report."""
    clear_screen()
    print("\n" + "="*60)
    print("\n🎤 AVATAR SPEECH RECOGNITION TEST SUITE")
    print("\nThis suite will test 10 different speech recognition scenarios")
    print("to evaluate the overall performance of your extension.")
    print("="*60)
    
    # Launch Chrome with the extension
    if not launch_chrome_with_extension():
        print("❌ Failed to launch Chrome. Test aborted.")
        return
    
    print("\n✅ Chrome launched! Please wait for the page to load completely.")
    input("\nPress ENTER when Scratch editor and extension have loaded...")
    
    # Step 1: Check UI
    clear_screen()
    print("\n" + "="*60)
    print("\n🔍 STEP 1: INITIAL SETUP")
    print("\nVerify the following:")
    print("1. Avatar container is visible in the Scratch editor")
    print("2. Mic button is visible and clickable")
    print("3. DevTools Console panel is open (switch to Console tab if needed)")
    print("="*60)
    
    ui_check = input("\nAre the UI elements visible and DevTools open? (y/n): ").lower()
    if ui_check != 'y':
        print("❌ UI elements not visible or DevTools not open. Test aborted.")
        return
    
    # Initialize results storage
    results = []
    
    # Run each test case
    for index, test_case in enumerate(TEST_CASES, 1):
        clear_screen()
        print("\n" + "="*60)
        print(f"\n🔤 TEST CASE {index}/10: {test_case['name']}")
        print("\nPurpose:", test_case['purpose'])
        print("\nPlease follow these steps:")
        print("1. Click the mic button in the avatar panel")
        print("2. When the button turns RED, say clearly:")
        print(f"\n   \"{test_case['phrase']}\"")
        print("\n3. Click the mic button again to stop recording")
        print("4. Check the console for \"Heard: [your speech]\"")
        print("="*60)
        
        proceed = input("\nPress ENTER when ready to begin this test case...")
        
        # Run the test for this phrase
        print(f"\n🎤 Now testing: \"{test_case['phrase']}\"")
        input("\nPress ENTER after completing the test steps...")
        
        # Collect results
        console_text = input("\nEnter text from console (after \"Heard:\") : ").strip()
        speech_bubble_text = input("Enter text from speech bubble (if any) : ").strip()
        
        # Determine which text to use for accuracy calculation
        recognized_text = console_text if console_text else speech_bubble_text
        
        # Calculate accuracy
        accuracy = calculate_accuracy(test_case['phrase'], recognized_text)
        
        # Store the results
        test_result = {
            "test_name": test_case['name'],
            "expected": test_case['phrase'],
            "console": console_text,
            "bubble": speech_bubble_text,
            "accuracy": accuracy
        }
        results.append(test_result)
        
        # Show individual test results
        print("\n" + "-"*40)
        print(f"Test {index} Results:")
        print(f"Accuracy: {accuracy:.1f}%")
        print("-"*40)
        
        if index < len(TEST_CASES):
            input("\nPress ENTER to continue to the next test case...")
    
    # Generate final report
    generate_report(results)

def generate_report(results):
    """Generate a comprehensive test report."""
    clear_screen()
    
    # Calculate overall statistics
    total_accuracy = sum(result["accuracy"] for result in results)
    avg_accuracy = total_accuracy / len(results) if results else 0
    
    # Group results by performance
    excellent = [r for r in results if r["accuracy"] >= 90]
    good = [r for r in results if 70 <= r["accuracy"] < 90]
    poor = [r for r in results if r["accuracy"] < 70]
    
    # Generate report
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n" + "="*70)
    print("\n📊 SPEECH RECOGNITION TEST REPORT")
    print(f"\nGenerated: {timestamp}")
    print("="*70)
    
    print("\n📈 OVERALL PERFORMANCE")
    print(f"Average Accuracy: {avg_accuracy:.1f}%")
    print(f"Tests Conducted: {len(results)}")
    print(f"Excellent Results (≥90%): {len(excellent)}")
    print(f"Good Results (70-89%): {len(good)}")
    print(f"Poor Results (<70%): {len(poor)}")
    
    print("\n📋 DETAILED RESULTS")
    for i, result in enumerate(results, 1):
        print(f"\nTest {i}: {result['test_name']} - {result['accuracy']:.1f}%")
        print(f"  Expected: {result['expected']}")
        print(f"  Actual:   {result['console'] or result['bubble']}")
    
    print("\n💪 STRENGTHS")
    if excellent:
        print("Best performing test cases:")
        for result in sorted(excellent, key=lambda x: x["accuracy"], reverse=True)[:3]:
            print(f"  • {result['test_name']} ({result['accuracy']:.1f}%)")
    else:
        print("No exceptional strengths identified.")
    
    print("\n🔍 AREAS FOR IMPROVEMENT")
    if poor:
        print("Lowest performing test cases:")
        for result in sorted(poor, key=lambda x: x["accuracy"])[:3]:
            print(f"  • {result['test_name']} ({result['accuracy']:.1f}%)")
    else:
        print("No significant weaknesses identified.")
    
    print("\n💡 RECOMMENDATIONS")
    if avg_accuracy < 70:
        print("• Speech recognition accuracy needs significant improvement")
        print("• Consider adjusting microphone settings or environment")
    elif avg_accuracy < 85:
        print("• Overall performance is good but can be improved")
        print("• Focus on improving recognition of challenging phrases")
    else:
        print("• Speech recognition is performing well")
        print("• Fine-tune handling of special cases like technical terms")
    
    # Additional recommendations based on specific issues
    if any(r["console"] and not r["bubble"] for r in results):
        print("• Check the speech bubble display functionality - some recognized")
        print("  speech is not appearing in the speech bubble")
    
    print("\n" + "="*70)
    print("\n🏁 TEST SUITE COMPLETE")
    print("\nYou can close Chrome now.")
    print("="*70)
    
    # Save report to file
    try:
        report_file = f"speech_recognition_report_{timestamp.replace(':', '-').replace(' ', '_')}.txt"
        with open(report_file, 'w') as f:
            f.write(f"SPEECH RECOGNITION TEST REPORT\n")
            f.write(f"Generated: {timestamp}\n")
            f.write("="*50 + "\n\n")
            
            f.write("OVERALL PERFORMANCE\n")
            f.write(f"Average Accuracy: {avg_accuracy:.1f}%\n")
            f.write(f"Tests Conducted: {len(results)}\n\n")
            
            f.write("DETAILED RESULTS\n")
            for i, result in enumerate(results, 1):
                f.write(f"Test {i}: {result['test_name']} - {result['accuracy']:.1f}%\n")
                f.write(f"  Expected: {result['expected']}\n")
                f.write(f"  Actual:   {result['console'] or result['bubble']}\n\n")
        
        print(f"\nReport saved to {report_file}")
    except Exception as e:
        print(f"\nCould not save report to file: {e}")

if __name__ == "__main__":
    run_test_suite()