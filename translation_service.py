"""
Translation Service - Hybrid Thai to Chinese Translation
Uses googletrans (primary) with deep-translator fallback.
Handles googletrans async nature explicitly.
"""

import concurrent.futures
import asyncio
from typing import Optional, Tuple
from deep_translator import GoogleTranslator
from googletrans import Translator

class TranslationService:
    """Hybrid Thai-Chinese Translation Service"""
    
    SHORT_TEXT_THRESHOLD = 500
    
    def __init__(self):
        """Initialize translation service"""
        self._deep_translator = GoogleTranslator(source='th', target='zh-CN')
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._future: Optional[concurrent.futures.Future] = None

    def _translate_google_sync(self, text: str) -> str:
        """
        Wrapper to run googletrans synchronously.
        """
        try:
            # Instantiate here to avoid thread safety issues
            translator = Translator()
            result = translator.translate(text, src='th', dest='zh-cn')
            return result.text
        except Exception as e:
            raise RuntimeError(f"Googletrans error: {str(e)}")

    def translate(self, text: str) -> Tuple[str, str]:
        """
        Translate Thai text to Chinese using hybrid approach.
        Returns: (translated_text, translator_used)
        """
        text = text.strip()
        if not text:
            return "", "none"
        
        # Strategy: Use googletrans for short text, deep-translator for long text
        use_googletrans_first = len(text) <= self.SHORT_TEXT_THRESHOLD
        
        if use_googletrans_first:
            try:
                # Try Googletrans
                result = self._translate_google_sync(text)
                return result, "googletrans"
            except Exception as e:
                print(f"Googletrans failed ({e}), switching to fallback...")
                try:
                    # Fallback to Deep Translator
                    result = self._deep_translator.translate(text)
                    return result, "deep-translator (fallback)"
                except Exception as ex:
                    raise TranslationError(f"All translators failed. Google: {e}, Deep: {ex}")
        else:
            # Long text: Deep Translator first
            try:
                result = self._deep_translator.translate(text)
                return result, "deep-translator"
            except Exception:
                try:
                    result = self._translate_google_sync(text)
                    return result, "googletrans (fallback)"
                except Exception as ex:
                     raise TranslationError(f"All translators failed: {ex}")

    def translate_async(self, text: str) -> None:
        """Start translation in background thread"""
        self._future = self._executor.submit(self.translate, text)
    
    def get_translation_result(self, timeout: float = 30.0) -> Tuple[str, str]:
        """Get result from background translation."""
        if self._future is None:
            raise TranslationError("No translation in progress")
        
        try:
            return self._future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise TranslationError("Translation timed out")
        except Exception as e:
            raise TranslationError(f"Translation failed: {e}")
    
    def is_translation_done(self) -> bool:
        """Check if background translation is complete"""
        return self._future is not None and self._future.done()
    
    def shutdown(self):
        """Cleanup executor"""
        self._executor.shutdown(wait=False)


class TranslationError(Exception):
    """Custom exception for translation errors"""
    pass
