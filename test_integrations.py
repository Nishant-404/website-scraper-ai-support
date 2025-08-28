#!/usr/bin/env python3
"""
Test script for WhatsApp and Email integrations
"""

import json
import os
from integrations.integration_manager import IntegrationManager

def test_integrations():
    """Test all integrations"""
    print("🧪 Testing WhatsApp and Email Integrations...")
    print("=" * 60)
    
    # Initialize integration manager
    try:
        manager = IntegrationManager()
        print("✅ Integration Manager initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Integration Manager: {e}")
        return
    
    # Test all integrations
    print("\n🔍 Testing Integration Connections...")
    test_results = manager.test_integrations()
    
    print("\n📊 Test Results:")
    print(json.dumps(test_results, indent=2))
    
    # Test chatbot specifically
    print("\n🤖 Testing AI Chatbot...")
    if manager.chatbot:
        test_questions = [
            "What are your shipping policies?",
            "How can I contact support?",
            "Tell me about your products"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: {question}")
            response = manager.chatbot.get_response(question)
            if response['success']:
                print(f"✅ Response: {response['response'][:100]}...")
                print(f"📚 Context sources: {len(response['relevant_context'])}")
            else:
                print(f"❌ Error: {response.get('error', 'Unknown error')}")
    
    # Show configuration status
    print("\n⚙️ Configuration Status:")
    config = manager.config
    
    print(f"WhatsApp: {'✅ Enabled' if config['whatsapp']['enabled'] else '❌ Disabled'}")
    if config['whatsapp']['enabled']:
        print(f"  Provider: {config['whatsapp']['provider']}")
        print(f"  Number: {config['whatsapp']['whatsapp_number']}")
    
    print(f"Email: {'✅ Enabled' if config['email']['enabled'] else '❌ Disabled'}")
    if config['email']['enabled']:
        print(f"  Provider: {config['email']['provider']}")
        print(f"  Address: {config['email']['email_address']}")
        print(f"  Monitoring: {'✅ On' if config['email']['monitoring'] else '❌ Off'}")
    
    print(f"Chatbot: {'✅ Ready' if manager.chatbot else '❌ Not Ready'}")
    if manager.chatbot:
        print(f"  Q&A Pairs: {len(manager.chatbot.qa_pairs)}")
        print(f"  Company: {config['chatbot']['company_name']}")
    
    # Show setup instructions
    print("\n📋 Setup Instructions:")
    print("=" * 60)
    
    if not config['whatsapp']['enabled']:
        print("\n📱 WhatsApp Setup:")
        print("1. Sign up for Twilio account: https://www.twilio.com/")
        print("2. Get WhatsApp Business API access")
        print("3. Add your credentials to .env file:")
        print("   TWILIO_ACCOUNT_SID=your_account_sid")
        print("   TWILIO_AUTH_TOKEN=your_auth_token")
        print("   WHATSAPP_NUMBER=whatsapp:+1234567890")
        print("4. Set 'enabled': true in integration_config.json")
    
    if not config['email']['enabled']:
        print("\n📧 Email Setup:")
        print("1. Use Gmail or Outlook for support email")
        print("2. Enable 2-factor authentication")
        print("3. Generate app password (not your regular password)")
        print("4. Add credentials to .env file:")
        print("   SUPPORT_EMAIL=your-support@gmail.com")
        print("   EMAIL_PASSWORD=your-app-password")
        print("5. Set 'enabled': true in integration_config.json")
    
    print("\n🚀 Once configured, your system will:")
    print("✅ Automatically respond to WhatsApp messages")
    print("✅ Monitor and reply to support emails")
    print("✅ Use AI to provide contextual responses")
    print("✅ Log all conversations for analytics")
    
    # Get analytics
    analytics = manager.get_analytics()
    print(f"\n📊 Current Analytics: {analytics}")

def simulate_whatsapp_message():
    """Simulate a WhatsApp message for testing"""
    print("\n📱 Simulating WhatsApp Message...")
    
    manager = IntegrationManager()
    
    # Simulate incoming message
    test_message = "What are your shipping policies?"
    test_number = "whatsapp:+919876543210"
    
    print(f"Incoming: {test_message}")
    
    # Handle message (without actually sending via WhatsApp)
    if manager.chatbot:
        response = manager.chatbot.get_response(test_message)
        if response['success']:
            print(f"AI Response: {response['response']}")
            print("✅ Would send via WhatsApp if configured")
        else:
            print(f"❌ AI Error: {response.get('error')}")
    else:
        print("❌ Chatbot not available")

def simulate_email_message():
    """Simulate an email message for testing"""
    print("\n📧 Simulating Email Message...")
    
    manager = IntegrationManager()
    
    # Simulate incoming email
    email_data = {
        'from': 'customer@example.com',
        'subject': 'Question about your products',
        'content': 'Hi, I would like to know more about your gaming mice. What options do you have?',
        'date': '2025-08-28',
        'id': 'test123'
    }
    
    print(f"From: {email_data['from']}")
    print(f"Subject: {email_data['subject']}")
    print(f"Content: {email_data['content']}")
    
    # Handle email (without actually sending)
    result = manager.handle_email_message(email_data)
    
    if result['success']:
        print(f"AI Response: {result['ai_response']}")
        print("✅ Would send via email if configured")
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    # Run main test
    test_integrations()
    
    # Run simulations
    simulate_whatsapp_message()
    simulate_email_message()
    
    print("\n🎉 Integration testing complete!")
    print("Configure your API keys to enable live functionality.")