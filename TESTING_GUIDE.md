# Refactoring Validation & Testing Guide

This document provides step-by-step instructions to validate that the equal-hand-treatment refactoring is working correctly.

---

## Pre-Testing Checklist

Before running tests, ensure:

- [ ] Code has been pulled/updated with refactoring changes
- [ ] Python environment is set up: `python -m pip install -r requirements.txt`
- [ ] Webcam is connected and working
- [ ] model.pkl exists (trained model)
- [ ] data/landmarks.csv exists (training data)
- [ ] All gesture images are in data/dataset/0-9/

---

## Test 1: Verify Code Changes

### Objective
Confirm that the right-hand preference code has been removed.

### Steps

1. Open `extractor.py` in an editor
2. Search for these (should NOT exist):
   - `_select_primary_index` ❌
   - `last_right_hand_landmarks` ❌
   - `last_right_hand_proto` ❌
   - `last_detected_handedness` ❌
   - `get_right_hand_landmarks` ❌

3. Search for these (SHOULD exist):
   - `extract_all` ✅
   - `draw_all_hands` ✅
   - `draw_hand_by_index` ✅
   - `No hand preference` (in docstring) ✅

### Expected Results

```
✓ All right-hand preference code removed
✓ New equal-treatment methods present
✓ Docstrings updated with "both hands equally"
```

---

## Test 2: Import Verification

### Objective
Verify the module imports without errors.

### Code
```python
# test_imports.py
import sys
sys.path.insert(0, '.')

try:
    from extractor import MediaPipeExtractor
    print("✓ extractor imports successfully")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

try:
    extractor = MediaPipeExtractor(mode=True)
    print("✓ MediaPipeExtractor initializes successfully")
except Exception as e:
    print(f"✗ Initialization failed: {e}")
    sys.exit(1)

# Check that old attributes don't exist
if hasattr(extractor, '_select_primary_index'):
    print("✗ ERROR: _select_primary_index still exists!")
    sys.exit(1)
else:
    print("✓ Old preference methods removed")

# Check that new methods exist
assert hasattr(extractor, 'extract_all'), "extract_all not found"
assert hasattr(extractor, 'draw_hand_by_index'), "draw_hand_by_index not found"
print("✓ New methods present")

print("\n✅ All import checks passed!")
```

### Run
```bash
python test_imports.py
```

### Expected Output
```
✓ extractor imports successfully
✓ MediaPipeExtractor initializes successfully
✓ Old preference methods removed
✓ New methods present

✅ All import checks passed!
```

---

## Test 3: Single Hand Detection (Right Hand Only)

### Objective
Test that right hand is correctly detected when only right hand is visible.

### Setup
- Have only your RIGHT hand visible to webcam
- Keep left side of frame empty
- Position right hand clearly in frame

### Code
```python
# test_single_right_hand.py
import cv2
import numpy as np
from extractor import MediaPipeExtractor

extractor = MediaPipeExtractor(mode=False)
cap = cv2.VideoCapture(0)

print("Testing RIGHT HAND ONLY detection...")
print("Please show ONLY your right hand to the camera.")
print("Press SPACE when ready with right hand visible")

frame_count = 0
right_hand_detected = False

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):
        # Capture 10 frames with hand visible
        print(f"Capturing frame {frame_count + 1}/10...")
        
        hands = extractor.extract_all(frame)
        extractor.draw_all_hands(frame)
        
        if hands:
            print(f"  → Detected {len(hands)} hand(s): "
                  f"{[h['label'] for h in hands]}")
            
            for hand in hands:
                if hand["label"] == "Right":
                    right_hand_detected = True
                    landmarks = hand["landmarks"]
                    print(f"  → Right hand landmarks shape: {landmarks.shape}")
                    assert landmarks.shape == (63,), \
                        f"Expected shape (63,), got {landmarks.shape}"
        
        frame_count += 1
        if frame_count >= 10:
            break
    
    cv2.imshow("Right Hand Test", frame)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

if right_hand_detected:
    print("\n✅ RIGHT HAND TEST PASSED")
    print("   Right hand was correctly detected and processed")
else:
    print("\n✗ RIGHT HAND TEST FAILED")
    print("   Right hand was NOT detected")
```

### Run
```bash
python test_single_right_hand.py
```

### Expected Output
```
Testing RIGHT HAND ONLY detection...
Please show ONLY your right hand to the camera.
Press SPACE when ready with right hand visible
Capturing frame 1/10...
  → Detected 1 hand(s): ['Right']
  → Right hand landmarks shape: (63,)
  ...
  [repeated 9 more times]

✅ RIGHT HAND TEST PASSED
   Right hand was correctly detected and processed
```

---

## Test 4: Single Hand Detection (Left Hand Only)

### Objective
Test that left hand is correctly detected when only left hand is visible.

### Setup
- Have only your LEFT hand visible to webcam
- Keep right side of frame empty
- Position left hand clearly in frame

### Code
```python
# test_single_left_hand.py
import cv2
import numpy as np
from extractor import MediaPipeExtractor

extractor = MediaPipeExtractor(mode=False)
cap = cv2.VideoCapture(0)

print("Testing LEFT HAND ONLY detection...")
print("Please show ONLY your left hand to the camera.")
print("Press SPACE when ready with left hand visible")

frame_count = 0
left_hand_detected = False

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):
        print(f"Capturing frame {frame_count + 1}/10...")
        
        hands = extractor.extract_all(frame)
        extractor.draw_all_hands(frame)
        
        if hands:
            print(f"  → Detected {len(hands)} hand(s): "
                  f"{[h['label'] for h in hands]}")
            
            for hand in hands:
                if hand["label"] == "Left":
                    left_hand_detected = True
                    landmarks = hand["landmarks"]
                    print(f"  → Left hand landmarks shape: {landmarks.shape}")
                    assert landmarks.shape == (63,), \
                        f"Expected shape (63,), got {landmarks.shape}"
        
        frame_count += 1
        if frame_count >= 10:
            break
    
    cv2.imshow("Left Hand Test", frame)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

if left_hand_detected:
    print("\n✅ LEFT HAND TEST PASSED")
    print("   Left hand was correctly detected and processed")
else:
    print("\n✗ LEFT HAND TEST FAILED")
    print("   Left hand was NOT detected")
```

### Run
```bash
python test_single_left_hand.py
```

### Expected Output
```
Testing LEFT HAND ONLY detection...
Please show ONLY your left hand to the camera.
Press SPACE when ready with left hand visible
Capturing frame 1/10...
  → Detected 1 hand(s): ['Left']
  → Left hand landmarks shape: (63,)
  ...
  [repeated 9 more times]

✅ LEFT HAND TEST PASSED
   Left hand was correctly detected and processed
```

---

## Test 5: Dual Hand Detection

### Objective
Test that both hands are detected simultaneously and processed independently.

### Setup
- Have BOTH hands visible to webcam
- Position both hands clearly in frame

### Code
```python
# test_dual_hands.py
import cv2
import numpy as np
from extractor import MediaPipeExtractor

extractor = MediaPipeExtractor(mode=False)
cap = cv2.VideoCapture(0)

print("Testing DUAL HAND detection...")
print("Please show BOTH your hands to the camera.")
print("Press SPACE when both hands are visible")

frame_count = 0
both_hands_detected = False
left_and_right = False

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):
        print(f"Capturing frame {frame_count + 1}/10...")
        
        hands = extractor.extract_all(frame)
        extractor.draw_all_hands(frame)
        
        if hands:
            print(f"  → Detected {len(hands)} hand(s)")
            
            labels = [h["label"] for h in hands]
            print(f"  → Labels: {labels}")
            
            if len(hands) == 2:
                both_hands_detected = True
                if set(labels) == {"Left", "Right"}:
                    left_and_right = True
                    print("  → Both LEFT and RIGHT hands detected ✓")
            
            # Verify landmarks
            for i, hand in enumerate(hands):
                landmarks = hand["landmarks"]
                label = hand["label"]
                print(f"  → Hand {i} ({label}): shape={landmarks.shape}, "
                      f"dtype={landmarks.dtype}")
                assert landmarks.shape == (63,), \
                    f"Hand {i}: Expected shape (63,), got {landmarks.shape}"
        
        frame_count += 1
        if frame_count >= 10:
            break
    
    cv2.imshow("Dual Hand Test", frame)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

if both_hands_detected and left_and_right:
    print("\n✅ DUAL HAND TEST PASSED")
    print("   Both LEFT and RIGHT hands detected and processed independently")
elif both_hands_detected:
    print("\n⚠ PARTIAL PASS")
    print("   Both hands detected but not both left and right")
else:
    print("\n✗ DUAL HAND TEST FAILED")
    print("   Could not detect both hands simultaneously")
```

### Run
```bash
python test_dual_hands.py
```

### Expected Output
```
Testing DUAL HAND detection...
Please show BOTH your hands to the camera.
Press SPACE when both hands are visible
Capturing frame 1/10...
  → Detected 2 hands
  → Labels: ['Left', 'Right']
  → Both LEFT and RIGHT hands detected ✓
  → Hand 0 (Left): shape=(63,), dtype=float32
  → Hand 1 (Right): shape=(63,), dtype=float32
  ...
  [repeated 9 more times]

✅ DUAL HAND TEST PASSED
   Both LEFT and RIGHT hands detected and processed independently
```

---

## Test 6: Preprocessing Pipeline (Backward Compatibility)

### Objective
Verify preprocessing still works without changes.

### Setup
- Ensure data/dataset/0-9/ contains gesture images
- Backup any existing data/landmarks.csv

### Code
```bash
# test_preprocessing.sh
echo "Testing preprocessing pipeline..."

# Run preprocessing
python preprocess.py

# Check output
if [ -f "data/landmarks.csv" ]; then
    echo "✓ landmarks.csv created"
    
    # Count rows (should be > 10)
    row_count=$(wc -l < data/landmarks.csv)
    echo "✓ landmarks.csv has $row_count rows"
    
    if [ $row_count -gt 10 ]; then
        echo "✅ PREPROCESSING TEST PASSED"
    else
        echo "✗ Not enough samples in landmarks.csv"
    fi
else
    echo "✗ landmarks.csv not created"
fi
```

### Run
```bash
bash test_preprocessing.sh
```

### Expected Output
```
Testing preprocessing pipeline...
✓ landmarks.csv created
✓ landmarks.csv has 245 rows
✅ PREPROCESSING TEST PASSED
```

---

## Test 7: Model Training (Backward Compatibility)

### Objective
Verify model training works and produces similar accuracy.

### Steps

1. Record baseline accuracy from previous run (if available)
2. Run training

### Code
```bash
echo "Testing model training..."

python train.py | tee train_output.txt

# Extract accuracy
if grep -q "Test Accuracy:" train_output.txt; then
    accuracy=$(grep "Test Accuracy:" train_output.txt | tail -1 | awk '{print $NF}')
    echo "✓ Model trained successfully"
    echo "✓ Test accuracy: $accuracy"
    echo "✅ TRAINING TEST PASSED"
else
    echo "✗ Training failed or accuracy not found"
fi
```

### Run
```bash
bash test_training.sh
```

### Expected Output
```
Testing model training...
...
[training output]
...
Test Accuracy: 0.9250
✓ Model trained successfully
✓ Test accuracy: 0.9250
✅ TRAINING TEST PASSED
```

---

## Test 8: Inference with Single Hand

### Objective
Verify real-time inference works with single hand.

### Code
```python
# test_inference_single.py
import cv2
import joblib
import numpy as np
from extractor import MediaPipeExtractor
from translator import DIGIT_TO_KANNADA

model = joblib.load("model.pkl")
extractor = MediaPipeExtractor(mode=False)
cap = cv2.VideoCapture(0)

print("Testing inference with SINGLE HAND...")
print("Show one hand and press SPACE to test")

single_hand_tested = False

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):
        hands = extractor.extract_all(frame)
        
        if len(hands) == 1:
            hand = hands[0]
            landmarks = hand["landmarks"]
            probs = model.predict_proba(landmarks.reshape(1, -1))[0]
            digit = model.predict(landmarks.reshape(1, -1))[0]
            confidence = np.max(probs)
            
            kannada = DIGIT_TO_KANNADA.get(str(digit), "?")
            
            print(f"Hand: {hand['label']}")
            print(f"Predicted digit: {digit}")
            print(f"Kannada: {kannada}")
            print(f"Confidence: {confidence:.1%}")
            
            single_hand_tested = True
            break
        else:
            print(f"Please show exactly 1 hand (detected {len(hands)})")
    
    cv2.imshow("Test", frame)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

if single_hand_tested:
    print("\n✅ SINGLE HAND INFERENCE TEST PASSED")
else:
    print("\n✗ SINGLE HAND INFERENCE TEST FAILED")
```

### Run
```bash
python test_inference_single.py
```

### Expected Output
```
Testing inference with SINGLE HAND...
Show one hand and press SPACE to test
Hand: Right
Predicted digit: 5
Kannada: ಐದು
Confidence: 78.5%

✅ SINGLE HAND INFERENCE TEST PASSED
```

---

## Test 9: Inference with Dual Hands

### Objective
Verify real-time inference works with both hands independently.

### Code
```python
# test_inference_dual.py
import cv2
import joblib
import numpy as np
from extractor import MediaPipeExtractor
from translator import DIGIT_TO_KANNADA

model = joblib.load("model.pkl")
extractor = MediaPipeExtractor(mode=False)
cap = cv2.VideoCapture(0)

print("Testing inference with BOTH HANDS...")
print("Show both hands and press SPACE to test")

dual_hand_tested = False

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):
        hands = extractor.extract_all(frame)
        
        if len(hands) == 2:
            print(f"\nDetected {len(hands)} hands:")
            
            for hand in hands:
                landmarks = hand["landmarks"]
                probs = model.predict_proba(landmarks.reshape(1, -1))[0]
                digit = model.predict(landmarks.reshape(1, -1))[0]
                confidence = np.max(probs)
                kannada = DIGIT_TO_KANNADA.get(str(digit), "?")
                
                print(f"  {hand['label']}:")
                print(f"    → Digit: {digit}")
                print(f"    → Kannada: {kannada}")
                print(f"    → Confidence: {confidence:.1%}")
            
            dual_hand_tested = True
            break
        else:
            print(f"Please show exactly 2 hands (detected {len(hands)})")
    
    cv2.imshow("Test", frame)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

if dual_hand_tested:
    print("\n✅ DUAL HAND INFERENCE TEST PASSED")
else:
    print("\n✗ DUAL HAND INFERENCE TEST FAILED")
```

### Run
```bash
python test_inference_dual.py
```

### Expected Output
```
Testing inference with BOTH HANDS...
Show both hands and press SPACE to test

Detected 2 hands:
  Left:
    → Digit: 3
    → Kannada: ಮೂರು
    → Confidence: 82.3%
  Right:
    → Digit: 7
    → Kannada: ಏಳು
    → Confidence: 91.5%

✅ DUAL HAND INFERENCE TEST PASSED
```

---

## Test 10: Full Main.py Runtime

### Objective
Verify main.py runs without errors with refactored code.

### Steps

1. Run main.py
2. Show right hand only - should predict
3. Show left hand only - should predict
4. Show both hands - should predict both
5. Press Q to quit

### Code
```bash
python main.py
```

### Expected Behavior

```
✓ Window opens without errors
✓ Shows webcam feed
✓ Shows hand skeleton overlay
✓ Shows predictions with confidence bars
✓ Shows Kannada text
✓ Shows "Active:" prediction
✓ Shows per-hand status lines for both hands
✓ FPS counter updates
✓ No errors in terminal
✓ Quitting with Q works
```

---

## Test Summary Report Template

Copy and fill out this template:

```
═══════════════════════════════════════════════════════════════
REFACTORING VALIDATION REPORT
═══════════════════════════════════════════════════════════════

Date: _______________
Tester: _______________
System: _______________

TEST RESULTS:
─────────────────────────────────────────────────────────────

Test 1: Code Changes                    [ ] PASS [ ] FAIL
Test 2: Import Verification             [ ] PASS [ ] FAIL
Test 3: Single Right Hand Detection     [ ] PASS [ ] FAIL
Test 4: Single Left Hand Detection      [ ] PASS [ ] FAIL
Test 5: Dual Hand Detection             [ ] PASS [ ] FAIL
Test 6: Preprocessing Pipeline          [ ] PASS [ ] FAIL
Test 7: Model Training                  [ ] PASS [ ] FAIL
Test 8: Single Hand Inference           [ ] PASS [ ] FAIL
Test 9: Dual Hand Inference             [ ] PASS [ ] FAIL
Test 10: Full Main.py Runtime           [ ] PASS [ ] FAIL

─────────────────────────────────────────────────────────────
SUMMARY:  [ ] ALL PASS  [ ] SOME FAIL  [ ] NEEDS DEBUG

Notes:
_________________________________________________________________

═══════════════════════════════════════════════════════════════
```

---

## Troubleshooting

### Issue: Tests fail with "No module named extractor"
**Solution**: Run tests from project root directory

### Issue: Model not found during inference tests
**Solution**: Ensure model.pkl exists - run `python train.py` first

### Issue: Webcam tests fail
**Solution**: Check camera permissions, close other camera apps

### Issue: Hands not detected
**Solution**: Improve lighting, move hands closer to camera

### Issue: Left hand keeps showing as "Right"
**Solution**: MediaPipe hand labeling is based on visual appearance, not position. Ensure good lighting and hand visibility.

---

## Conclusion

Once all tests pass:

✅ Equal-hand-treatment refactoring is complete  
✅ Code is backward compatible  
✅ Both hands work equally well  
✅ Ready for production use  

**Next Steps**: Deploy to users or proceed with additional features!
