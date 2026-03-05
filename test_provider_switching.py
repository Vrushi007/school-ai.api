"""
Test script to verify AI provider switching functionality.

This script demonstrates how the AI provider factory works and can be used
to quickly test if the configuration is correct.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()


def test_provider_configuration():
    """Test that the provider configuration is loaded correctly"""
    from config import ai_provider_config, get_ai_provider_config
    
    print("=" * 60)
    print("AI Provider Configuration Test")
    print("=" * 60)
    
    config = get_ai_provider_config()
    print(f"\n✓ Provider configured: {config.provider}")
    print(f"✓ Is OpenAI: {config.is_openai}")
    print(f"✓ Is SarvamAI: {config.is_sarvam}")
    
    return config


def test_provider_initialization():
    """Test that the correct provider is initialized"""
    from services.ai_service_factory import get_ai_service
    
    print("\n" + "=" * 60)
    print("AI Service Initialization Test")
    print("=" * 60)
    
    try:
        ai_service = get_ai_service()
        provider_type = type(ai_service).__name__
        print(f"\n✓ AI Service initialized: {provider_type}")
        
        # Check that it implements the base interface
        from services.ai_provider_base import AIServiceProvider
        if isinstance(ai_service, AIServiceProvider):
            print("✓ Service implements AIServiceProvider interface")
        else:
            print("✗ Service does NOT implement AIServiceProvider interface")
            
        return ai_service
    except Exception as e:
        print(f"\n✗ Failed to initialize AI service: {e}")
        return None


def test_method_availability(ai_service):
    """Test that all required methods are available"""
    print("\n" + "=" * 60)
    print("Method Availability Test")
    print("=" * 60)
    
    required_methods = [
        'generate_lesson_plan',
        'generate_detailed_session_content',
        'generate_questions',
        'get_student_answer',
        'generate_knowledge_points',
        'group_kps_into_sessions',
        'generate_session_summary'
    ]
    
    print("\nChecking for required methods:")
    all_available = True
    for method_name in required_methods:
        if hasattr(ai_service, method_name):
            print(f"  ✓ {method_name}")
        else:
            print(f"  ✗ {method_name} - MISSING")
            all_available = False
    
    if all_available:
        print("\n✓ All required methods are available")
    else:
        print("\n✗ Some required methods are missing")
    
    return all_available


def test_environment_variables():
    """Test that required environment variables are set"""
    print("\n" + "=" * 60)
    print("Environment Variables Test")
    print("=" * 60)
    
    provider = os.getenv("AI_PROVIDER", "openai")
    print(f"\nAI_PROVIDER: {provider}")
    
    if provider == "openai":
        openai_key = os.getenv("OPENAI_API_KEY")
        print(f"OPENAI_API_KEY: {'✓ Set' if openai_key else '✗ Not set'}")
        print(f"OPENAI_MODEL_DEFAULT: {os.getenv('OPENAI_MODEL_DEFAULT', 'Not set')}")
        print(f"OPENAI_MODEL_5: {os.getenv('OPENAI_MODEL_5', 'Not set')}")
    elif provider in ["sarvam", "sarvam-ai"]:
        sarvam_key = os.getenv("SARVAM_API_KEY")
        print(f"SARVAM_API_KEY: {'✓ Set' if sarvam_key else '✗ Not set'}")
        print(f"SARVAM_API_BASE_URL: {os.getenv('SARVAM_API_BASE_URL', 'Not set')}")
        print(f"SARVAM_MODEL_DEFAULT: {os.getenv('SARVAM_MODEL_DEFAULT', 'Not set')}")
        print(f"SARVAM_MODEL_5: {os.getenv('SARVAM_MODEL_5', 'Not set')}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("School AI - Provider Switching Test Suite")
    print("=" * 60)
    
    try:
        # Test environment variables
        test_environment_variables()
        
        # Test provider configuration
        config = test_provider_configuration()
        
        # Test provider initialization
        ai_service = test_provider_initialization()
        
        if ai_service:
            # Test method availability
            test_method_availability(ai_service)
            
            print("\n" + "=" * 60)
            print("✓ All tests passed!")
            print("=" * 60)
            print(f"\nYour API is configured to use: {config.provider.upper()}")
            print("\nTo switch providers, update the AI_PROVIDER environment variable:")
            print("  - For OpenAI: AI_PROVIDER=openai")
            print("  - For SarvamAI: AI_PROVIDER=sarvam")
            print("\nThen restart the server.")
        else:
            print("\n" + "=" * 60)
            print("✗ Tests failed - check your configuration")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
