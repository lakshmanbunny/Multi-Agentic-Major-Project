"""
Test script for Browser Agent

Tests the Colab automation.
"""

import asyncio
import httpx

async def test_browser_agent():
    """Test the browser agent execute endpoint"""
    
    # Simple test code
    test_code = """
import pandas as pd
import matplotlib.pyplot as plt

# Create sample data
data = {'A': [1, 2, 3, 4, 5], 'B': [10, 20, 30, 40, 50]}
df = pd.DataFrame(data)

print("DataFrame created:")
print(df)

# Plot
plt.figure(figsize=(8, 4))
plt.plot(df['A'], df['B'], marker='o')
plt.title('Test Plot')
plt.xlabel('A')
plt.ylabel('B')
plt.savefig('test_plot.png')
print("\\nPlot saved!")
"""
    
    print("=" * 70)
    print("🧪 Testing Browser Agent - Colab Automation")
    print("=" * 70)
    print(f"\n📝 Code to execute ({len(test_code)} chars):")
    print("-" * 70)
    print(test_code[:200] + "...")
    print("-" * 70)
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            print("\n▶️ Sending code to Browser Agent...")
            
            response = await client.post(
                "http://localhost:8001/execute",
                json={"code": test_code}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ SUCCESS!")
                print(f"Status: {result['status']}")
                print(f"Screenshot: {result['screenshot']}")
                print(f"Message: {result['message']}")
            else:
                print(f"\n❌ ERROR: {response.status_code}")
                print(response.text)
    
    except Exception as e:
        print(f"\n❌ Failed to connect: {e}")
        print("\nMake sure the browser agent is running:")
        print("  python services/browser_agent/src/main.py")

if __name__ == "__main__":
    asyncio.run(test_browser_agent())
