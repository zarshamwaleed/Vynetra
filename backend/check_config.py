import sys
sys.path.append('.')

from app.core.config import settings

print("=" * 60)
print("🔍 Checking Configuration")
print("=" * 60)

print(f"\n📋 GROQ_API_KEY: {'✅' if settings.GROQ_API_KEY else '❌'} {settings.GROQ_API_KEY[:20] if settings.GROQ_API_KEY else 'Not set'}...")
print(f"📋 GOOGLE_API_KEY: {'✅' if settings.GOOGLE_API_KEY else '❌'} {settings.GOOGLE_API_KEY[:20] if settings.GOOGLE_API_KEY else 'Not set'}...")
print(f"📋 OPENROUTER_API_KEY: {'✅' if settings.OPENROUTER_API_KEY else '❌'} {settings.OPENROUTER_API_KEY[:20] if settings.OPENROUTER_API_KEY else 'Not set'}...")
print(f"📋 LLM_PROVIDER: {settings.LLM_PROVIDER}")
print(f"📋 GROQ_MODEL: {settings.GROQ_MODEL}")
print(f"📋 GEMINI_MODEL: {settings.GEMINI_MODEL}")
print(f"📋 OPENROUTER_MODEL: {settings.OPENROUTER_MODEL}")

print("\n" + "=" * 60)
