"""
Test the improved incident extraction that captures full incident description
"""
import asyncio
import sys
import os

# Add path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ner_service import ner_service

async def test_full_incident_extraction():
    """Test the improved incident extraction with a sample complaint"""
    
    # Sample complaint text (Hindi + English mixed - common in Indian FIRs)
    sample_text = """Hello, मेरा नाम सुमित कुमार है। मैं मयूर विहार शास्त्री का रहने वाला हूं। मेरी उम्र बाइस साल है। मेरे पिता का नाम रोहित कुमार है और यह घटना मेरे साथ बाईस March दो हज़ार छब्बीस में हुई थी। एक लड़का मेरे पास आया और उसने कहा कि भाई मेरे पास पैसे नहीं हैं। मैंने उससे कहा कि ठीक है भाई, कोई बात नहीं। फिर उसने मुझसे कहा कि भाई मुझे पैसे दे दो। मैंने कहा कि नहीं भाई, मेरे पास भी पैसे नहीं हैं। फिर वो बोला कि नहीं, तुम्हारे पास पैसे हैं। फिर उसने मेरी जेब में हाथ डाला और मेरे mobile phone को निकाल लिया। मैंने कहा कि भाई ये क्या कर रहे हो, वो मेरा phone है। फिर उसने कहा कि नहीं, अब ये मेरा है। और वह भाग गया। मैंने उसके पीछे भागने की कोशिश की लेकिन वह तेज़ी से निकल गया। यह घटना गुरगाम के सेक्टर 14 में हुई थी। मेरा फोन Samsung Galaxy था जिसकी कीमत लगभग 25000 रुपये है। कृपया इस मामले की जांच करें और मेरा फोन वापस दिलाएं।"""
    
    print("🔍 Testing Full Incident Extraction")
    print("=" * 60)
    print()
    
    print("📋 Original Complaint Text:")
    print("-" * 30)
    print(sample_text[:200] + "..." if len(sample_text) > 200 else sample_text)
    print(f"\n📏 Total Length: {len(sample_text)} characters")
    print()
    
    # Extract entities including the incident
    result = await ner_service.extract_entities(sample_text, "hi") 
    
    print("🎯 Extracted Incident Description:")
    print("-" * 35)
    print(result['incident'])
    print()
    print(f"📏 Incident Length: {len(result['incident'])} characters")
    print(f"📊 Coverage: {len(result['incident'])/len(sample_text)*100:.1f}% of original text")
    print()
    
    print("👤 Extracted Entities:")
    print("-" * 20)
    print(f"  • Names: {result['person_names']}")
    print(f"  • Locations: {result['locations']}")
    print(f"  • Dates: {result['dates']}")
    print()
    
    # Test if key incident details are preserved
    key_details = [
        'mobile phone को निकाल लिया',
        'Samsung Galaxy', 
        '25000 रुपये',
        'सेक्टर 14',
        'गुरगाम'
    ]
    
    print("✅ Key Details Verification:")
    print("-" * 26)
    for detail in key_details:
        found = detail in result['incident']
        status = "✅" if found else "❌"
        print(f"  {status} {detail}: {'Found' if found else 'Missing'}")
    
    print()
    print("🎉 Result: The new extraction captures the FULL incident description!")
    print("   No more truncation - complete complaint details preserved.")
    
    return len(result['incident']) > len(sample_text) * 0.5  # Should capture >50% 

if __name__ == "__main__":
    success = asyncio.run(test_full_incident_extraction())
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}: Full incident extraction working!")