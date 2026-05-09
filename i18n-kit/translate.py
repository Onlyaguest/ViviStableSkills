#!/usr/bin/env python3
"""
AI-powered translation for i18n-kit
Automatically translate zh-CN.json to multiple languages using Gemini
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime


# Language configurations
LANGUAGES = {
    "en-US": {"name": "English", "prompt": "English"},
    "ja-JP": {"name": "Japanese", "prompt": "Japanese"},
    "ko-KR": {"name": "Korean", "prompt": "Korean"},
    "es-ES": {"name": "Spanish", "prompt": "Spanish"},
    "fr-FR": {"name": "French", "prompt": "French"},
    "de-DE": {"name": "German", "prompt": "German"},
}


class TranslationStats:
    """Track translation statistics"""
    def __init__(self):
        self.start_time = time.time()
        self.total_texts = 0
        self.translated_texts = 0
        self.failed_texts = 0
        self.api_calls = 0
        self.total_tokens = 0
        
    def elapsed(self):
        return time.time() - self.start_time
    
    def to_dict(self):
        return {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(self.elapsed(), 2),
            "total_texts": self.total_texts,
            "translated_texts": self.translated_texts,
            "failed_texts": self.failed_texts,
            "api_calls": self.api_calls,
            "estimated_tokens": self.total_tokens,
        }


def translate_with_gemini(texts: list[str], target_lang: str, batch_size: int = 20, stats: TranslationStats = None) -> list[str]:
    """Translate a list of Chinese texts to target language using Gemini"""
    try:
        import google.generativeai as genai
    except ImportError:
        print("Error: google-generativeai not installed", file=sys.stderr)
        print("Run: pip install google-generativeai", file=sys.stderr)
        sys.exit(1)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    
    # Try different model names in order
    model_names = [
        "models/gemini-2.5-flash",
        "models/gemini-flash-latest",
        "models/gemini-2.0-flash",
        "gemini-flash-latest",
    ]
    
    model = None
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            # Test with a simple prompt
            test_response = model.generate_content("Hello")
            print(f"  ✓ Using model: {model_name}")
            break
        except Exception as e:
            continue
    
    if model is None:
        print("Error: Could not initialize any Gemini model", file=sys.stderr)
        print("Available models:", file=sys.stderr)
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f"  - {m.name}", file=sys.stderr)
        except:
            pass
        sys.exit(1)
    
    lang_config = LANGUAGES.get(target_lang, {"prompt": target_lang})
    target_language = lang_config["prompt"]
    
    results = []
    
    # Process in batches
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        # Create prompt
        prompt = f"""Translate the following Chinese texts to {target_language}. Keep the meaning accurate and natural.
Return ONLY a JSON array of translated strings, in the same order.
Do not add any explanation or markdown formatting.

Input texts:
"""
        prompt += json.dumps(batch, ensure_ascii=False, indent=2)
        
        if stats:
            stats.api_calls += 1
            # Rough token estimation: ~1.5 tokens per character for Chinese
            stats.total_tokens += len(prompt) * 1.5
        
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            if stats:
                stats.total_tokens += len(text) * 1.5
            
            # Extract JSON from markdown code blocks if present
            if text.startswith("```"):
                lines = text.split("\n")
                # Remove first line (```json or ```) and last line (```)
                text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
            
            translated = json.loads(text)
            
            if not isinstance(translated, list) or len(translated) != len(batch):
                print(f"Warning: batch {i//batch_size + 1} returned invalid format", file=sys.stderr)
                results.extend(batch)  # Fallback: keep original
                if stats:
                    stats.failed_texts += len(batch)
            else:
                results.extend(translated)
                if stats:
                    stats.translated_texts += len(batch)
                print(f"  ✓ Batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size} done")
                
        except Exception as e:
            print(f"Warning: batch {i//batch_size + 1} failed: {e}", file=sys.stderr)
            results.extend(batch)  # Fallback: keep original
            if stats:
                stats.failed_texts += len(batch)
    
    return results


def save_log(root: Path, stats: TranslationStats, target_langs: list[str]):
    """Save translation log"""
    log_dir = root / "i18n" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"translate-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    
    log_data = {
        **stats.to_dict(),
        "target_languages": target_langs,
    }
    
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Log saved: {log_file}")
    return log_file


def main():
    parser = argparse.ArgumentParser(description="Auto-translate i18n dictionary using AI")
    parser.add_argument("--root", type=Path, required=True, help="Project root directory")
    parser.add_argument("--source", default="zh-CN", help="Source language (default: zh-CN)")
    parser.add_argument("--targets", help="Target languages (comma-separated, e.g., en-US,ja-JP,ko-KR)")
    parser.add_argument("--target", help="Single target language (for backward compatibility)")
    parser.add_argument("--batch-size", type=int, default=20, help="Translation batch size")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--list-languages", action="store_true", help="List supported languages")
    
    args = parser.parse_args()
    
    # List languages
    if args.list_languages:
        print("Supported languages:")
        for code, info in LANGUAGES.items():
            print(f"  {code}: {info['name']}")
        return
    
    # Determine target languages
    if args.targets:
        target_langs = [lang.strip() for lang in args.targets.split(",")]
    elif args.target:
        target_langs = [args.target]
    else:
        # Default: all supported languages
        target_langs = list(LANGUAGES.keys())
    
    # Load source dictionary
    i18n_dir = args.root / "i18n"
    source_file = i18n_dir / f"{args.source}.json"
    
    if not source_file.exists():
        print(f"Error: Source dictionary not found: {source_file}", file=sys.stderr)
        sys.exit(1)
    
    with open(source_file, "r", encoding="utf-8") as f:
        source_dict = json.load(f)
    
    print(f"📖 Loaded {len(source_dict)} entries from {source_file}")
    print(f"🌐 Target languages: {', '.join(target_langs)}")
    print()
    
    stats = TranslationStats()
    stats.total_texts = len(source_dict) * len(target_langs)
    
    # Translate to each target language
    for target_lang in target_langs:
        print(f"🔄 Translating to {LANGUAGES.get(target_lang, {}).get('name', target_lang)} ({target_lang})...")
        
        target_file = i18n_dir / f"{target_lang}.json"
        
        # Load existing translations if any
        existing_dict = {}
        if target_file.exists():
            with open(target_file, "r", encoding="utf-8") as f:
                existing_dict = json.load(f)
            print(f"  📝 Found existing {target_lang}.json with {len(existing_dict)} entries")
        else:
            print(f"  📝 Creating new {target_lang}.json")
        
        # Find texts that need translation
        texts_to_translate = []
        keys_to_translate = []
        
        for key, text in source_dict.items():
            if key not in existing_dict or existing_dict[key] == text:
                # Not translated or still in Chinese
                texts_to_translate.append(text)
                keys_to_translate.append(key)
        
        if not texts_to_translate:
            print(f"  ✓ All entries already translated")
            continue
        
        print(f"  🤖 Translating {len(texts_to_translate)} entries...")
        
        if args.dry_run:
            print(f"  [DRY RUN] Would translate {len(texts_to_translate)} entries")
            continue
        
        # Translate
        translated_texts = translate_with_gemini(texts_to_translate, target_lang, args.batch_size, stats)
        
        # Update dictionary
        target_dict = existing_dict.copy()
        for key, translated in zip(keys_to_translate, translated_texts):
            target_dict[key] = translated
        
        # Write to file
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(target_dict, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ Wrote {len(target_dict)} entries to {target_file}")
        
        # Show sample translations
        print(f"\n  📋 Sample translations:")
        for i, (key, translated) in enumerate(zip(keys_to_translate[:3], translated_texts[:3])):
            original = source_dict[key]
            print(f"    {i+1}. {original}")
            print(f"       → {translated}")
        if len(keys_to_translate) > 3:
            print(f"    ... and {len(keys_to_translate) - 3} more")
        print()
    
    # Save log
    if not args.dry_run:
        log_file = save_log(args.root, stats, target_langs)
        
        # Print summary
        print(f"\n🎉 All translations complete!")
        print(f"   Duration: {stats.elapsed():.1f}s")
        print(f"   API calls: {stats.api_calls}")
        print(f"   Estimated tokens: ~{stats.total_tokens:.0f}")
        print(f"   Success rate: {stats.translated_texts}/{stats.total_texts} ({100*stats.translated_texts/stats.total_texts:.1f}%)")


if __name__ == "__main__":
    main()
