Pro"""
Test script to verify AWS Bedrock access and Claude 3 integration.
Run this to confirm your setup is working before building the full application.
"""

import boto3
import json
from botocore.exceptions import ClientError

def test_bedrock_access():
    """Test basic Bedrock access and list available models."""
    print("🔍 Testing AWS Bedrock access...\n")
    
    try:
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        
        # List all foundation models
        response = bedrock.list_foundation_models()
        
        # Filter for Claude models
        claude_models = [
            model for model in response['modelSummaries']
            if 'claude' in model['modelId'].lower()
        ]
        
        if claude_models:
            print("✅ SUCCESS! Found Claude models:")
            for model in claude_models:
                status = model['modelLifecycle']['status']
                print(f"   • {model['modelId']}")
                print(f"     Name: {model['modelName']}")
                print(f"     Provider: {model['providerName']}")
                print(f"     Status: {status}")
                print()
            return True
        else:
            print("⚠️  No Claude models found. Model access may not be approved yet.")
            print("   Go to: https://console.aws.amazon.com/bedrock/home?#/modelaccess")
            print("   Request access to 'Anthropic' models\n")
            return False
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print("❌ ERROR: Access Denied to Bedrock")
            print("   Check your IAM permissions - need 'bedrock:ListFoundationModels'\n")
        else:
            print(f"❌ ERROR: {e.response['Error']['Message']}\n")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}\n")
        return False


def test_bedrock_invoke():
    """Test invoking Claude 3 Haiku model."""
    print("🧪 Testing Claude 3 Haiku invocation...\n")
    
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Model ID for Claude 3 Haiku
        model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
        
        # Simple test prompt
        prompt = "Extract the following information from this medical note: Patient Name, Diagnosis. Medical Note: 'John Doe was diagnosed with Type 2 Diabetes.'"
        
        # Prepare request body (Claude 3 format)
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
        })
        
        # Invoke the model
        print(f"   Sending request to: {model_id}")
        print(f"   Prompt: {prompt[:100]}...\n")
        
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=body
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        print("✅ SUCCESS! Claude 3 Haiku response:")
        print("─" * 60)
        print(response_body['content'][0]['text'])
        print("─" * 60)
        
        # Print usage stats
        usage = response_body.get('usage', {})
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        
        print(f"\n📊 Token Usage:")
        print(f"   Input tokens: {input_tokens}")
        print(f"   Output tokens: {output_tokens}")
        
        # Estimate cost (Claude 3 Haiku pricing)
        input_cost = (input_tokens / 1000) * 0.00025  # $0.00025 per 1K tokens
        output_cost = (output_tokens / 1000) * 0.00125  # $0.00125 per 1K tokens
        total_cost = input_cost + output_cost
        
        print(f"   Estimated cost: ${total_cost:.6f}")
        print()
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'AccessDeniedException':
            print("❌ ERROR: Access Denied to invoke Bedrock model")
            print("   Possible causes:")
            print("   1. Model access not yet approved - check Bedrock console")
            print("   2. Missing IAM permission: 'bedrock:InvokeModel'")
            print(f"   Details: {error_message}\n")
        elif error_code == 'ResourceNotFoundException':
            print("❌ ERROR: Model not found")
            print(f"   The model '{model_id}' may not be available in your region")
            print("   Try region: us-east-1 or us-west-2\n")
        else:
            print(f"❌ ERROR: {error_code}")
            print(f"   {error_message}\n")
        
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}\n")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("  AWS BEDROCK INTEGRATION TEST")
    print("=" * 60)
    print()
    
    # Test 1: List models
    list_success = test_bedrock_access()
    
    if not list_success:
        print("⚠️  Fix model access issues before proceeding.\n")
        return
    
    print()
    
    # Test 2: Invoke Claude
    invoke_success = test_bedrock_invoke()
    
    print()
    print("=" * 60)
    
    if list_success and invoke_success:
        print("✅ ALL TESTS PASSED!")
        print("   Your Bedrock setup is working correctly.")
        print("   Ready to start building the application! 🚀")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("   Review error messages above and fix issues.")
    
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
