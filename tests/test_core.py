import sys, tempfile, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'lib'))
import lingokey_core as l

assert l.detect_language('مرحبا') == 'ar'
assert l.detect_language('hello') == 'en'
assert l.detect_language('hello مرحبا') == 'mixed'
assert l.keyboard_fix('sghl', 'en2ar') == 'سلام'
assert l.keyboard_fix('سلام', 'ar2en') == 'sghl'
assert l.translate('مرحبا') == 'Hello'
assert l.translate('How are you?') == 'كيف حالك'
assert l.suggest('ModuleNotFoundError: No module named requests')
print('ALL TESTS PASSED')
