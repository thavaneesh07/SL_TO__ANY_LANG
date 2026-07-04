# Equal-Hand Treatment: Usage Patterns & Best Practices

This guide shows how to properly use the refactored Sign2Kannada system that treats left and right hands equally.

---

## Quick Reference

| Task | Code | Notes |
|------|------|-------|
| Extract all hands | `hands = extractor.extract_all(frame)` | ✅ Recommended for main.py |
| Extract single hand | `landmark = extractor.extract(frame)` | ⚠️ Legacy, preprocessing only |
| Draw all hands | `extractor.draw_all_hands(frame)` | ✅ Recommended |
| Draw specific hand | `extractor.draw_hand_by_index(frame, 0)` | ✅ For custom UI |
| Get hand label | `hand["label"]` (from extract_all output) | Returns "Left" or "Right" |
| Get landmarks | `hand["landmarks"]` (from extract_all output) | 63-dim numpy array |

---

## Pattern 1: Processing Both Hands Equally (Recommended)

### Use Case
- Real-time inference where you want fair treatment of both hands
- Multi-hand gesture recognition
- User's dominant hand is unknown

### Code Example

```python
from pathlib import Path
import cv2
import joblib
import numpy as np
from extractor import MediaPipeExtractor
from translator import DIGIT_TO_KANNADA

# Setup
model = joblib.load("model.pkl")
extractor = MediaPipeExtractor(mode=False)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # PATTERN: Extract ALL hands, no preference
    hands = extractor.extract_all(frame)
    
    # Draw all hands on frame
    extractor.draw_all_hands(frame)
    
    # Process each hand independently
    predictions = {}
    for hand_idx, hand_data in enumerate(hands):
        handedness = hand_data["label"]  # "Left" or "Right"
        landmarks = hand_data["landmarks"]  # 63-dim vector
        
        # Make prediction for this hand
        digit = model.predict(landmarks.reshape(1, -1))[0]
        prob = model.predict_proba(landmarks.reshape(1, -1))[0]
        confidence = np.max(prob)
        
        # Store result with hand identity
        hand_key = f"{handedness}_Hand"
        predictions[hand_key] = {
            "digit": digit,
            "confidence": confidence
        }
    
    # Render predictions for all hands
    y_offset = 50
    for hand_key, result in predictions.items():
        text = f"{hand_key}: {result['digit']} ({result['confidence']:.0%})"
        cv2.putText(frame, text, (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2)
        y_offset += 30
    
    cv2.imshow("Dual Hand Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
extractor.close()
cv2.destroyAllWindows()
```

---

## Pattern 2: Processing Right Hand Only

### Use Case
- Legacy system that only cares about right hand
- Right-handed exclusive use case
- Backward compatibility requirement

### Code Example

```python
hands = extractor.extract_all(frame)

# Filter for right hand only
right_hands = [h for h in hands if h["label"].lower() == "right"]

if right_hands:
    # Use first (usually only) right hand
    landmarks = right_hands[0]["landmarks"]
    digit = model.predict(landmarks.reshape(1, -1))[0]
else:
    # No right hand detected
    digit = None

# Draw all hands for debugging, but only process right
extractor.draw_all_hands(frame)
```

---

## Pattern 3: Processing Left Hand Only

### Use Case
- Left-handed user
- Accessibility for left-dominant users
- Explicit left-hand-only configuration

### Code Example

```python
hands = extractor.extract_all(frame)

# Filter for left hand only
left_hands = [h for h in hands if h["label"].lower() == "left"]

if left_hands:
    # Use first (usually only) left hand
    landmarks = left_hands[0]["landmarks"]
    digit = model.predict(landmarks.reshape(1, -1))[0]
else:
    # No left hand detected
    digit = None

# Draw all hands for debugging, but only process left
extractor.draw_all_hands(frame)
```

---

## Pattern 4: Hand Agreement Voting

### Use Case
- High-confidence predictions requiring hand agreement
- Both hands must agree before committing to prediction
- Reduces false positives

### Code Example

```python
from collections import Counter

hands = extractor.extract_all(frame)

if len(hands) == 2:
    # Both hands visible - check agreement
    predictions = []
    for hand in hands:
        landmarks = hand["landmarks"]
        digit = model.predict(landmarks.reshape(1, -1))[0]
        predictions.append(digit)
    
    # Both hands agree?
    if predictions[0] == predictions[1]:
        agreed_digit = predictions[0]
        confidence = "HIGH"  # Both hands agree!
    else:
        agreed_digit = None
        confidence = "CONFLICTING"
else:
    # Single hand or no hands
    if hands:
        landmarks = hands[0]["landmarks"]
        agreed_digit = model.predict(landmarks.reshape(1, -1))[0]
        confidence = "SINGLE"
    else:
        agreed_digit = None
        confidence = "NONE"

print(f"Prediction: {agreed_digit}, Confidence: {confidence}")
```

---

## Pattern 5: Hand Dominance Detection

### Use Case
- Automatically detect which hand the user prefers
- Adapt to left-handed vs right-handed users
- Personalization

### Code Example

```python
from collections import defaultdict

hand_detection_counts = defaultdict(int)

# Run for N frames to accumulate statistics
for _ in range(100):
    ret, frame = cap.read()
    if not ret:
        break
    
    hands = extractor.extract_all(frame)
    for hand in hands:
        hand_label = hand["label"]  # "Left" or "Right"
        hand_detection_counts[hand_label] += 1

# Which hand is more often visible?
if hand_detection_counts["Right"] > hand_detection_counts["Left"]:
    dominant_hand = "Right"
    print("User appears to be right-handed")
elif hand_detection_counts["Left"] > hand_detection_counts["Right"]:
    dominant_hand = "Left"
    print("User appears to be left-handed")
else:
    dominant_hand = None
    print("User is ambidextrous or no preference detected")

# Now use dominant_hand for processing
```

---

## Pattern 6: Drawing Specific Hands

### Use Case
- Custom UI where you want to highlight specific hands
- Debugging: draw only detected hand
- Multi-hand scenario with special rendering

### Code Example

```python
hands = extractor.extract_all(frame)

# Option A: Draw all hands (simplest)
extractor.draw_all_hands(frame)

# Option B: Draw specific hand by index
if len(hands) >= 1:
    extractor.draw_hand_by_index(frame, hand_index=0)  # Draw first hand

if len(hands) >= 2:
    extractor.draw_hand_by_index(frame, hand_index=1)  # Draw second hand

# Option C: Custom rendering per hand
for hand_idx, hand in enumerate(hands):
    label = hand["label"]
    color = (0, 255, 0) if label == "Right" else (255, 0, 0)
    # Your custom drawing code here
```

---

## Pattern 7: Per-Hand Confidence Tracking

### Use Case
- Different confidence thresholds per hand
- Track each hand's stability separately
- Independent filtering per hand

### Code Example

```python
from collections import deque

# Track history per hand
hand_histories = {}
HISTORY_SIZE = 9
CONFIDENCE_THRESHOLD = 0.5

hands = extractor.extract_all(frame)

for hand in hands:
    hand_label = hand["label"]
    landmarks = hand["landmarks"]
    
    # Initialize history for this hand if new
    if hand_label not in hand_histories:
        hand_histories[hand_label] = deque(maxlen=HISTORY_SIZE)
    
    # Get prediction
    probs = model.predict_proba(landmarks.reshape(1, -1))[0]
    digit = model.predict(landmarks.reshape(1, -1))[0]
    confidence = np.max(probs)
    
    # Track if confidence is high enough
    if confidence >= CONFIDENCE_THRESHOLD:
        hand_histories[hand_label].append(digit)
    
    # Show stabilized prediction for this hand
    if len(hand_histories[hand_label]) > 0:
        most_common = max(set(hand_histories[hand_label]),
                         key=hand_histories[hand_label].count)
        print(f"{hand_label}: {most_common} "
              f"(history: {len(hand_histories[hand_label])}/{HISTORY_SIZE})")
```

---

## Pattern 8: Multi-Digit Recognition from Both Hands

### Use Case
- Left hand = tens digit, Right hand = ones digit
- Two-hand compound gestures
- Coordinate predictions from both hands

### Code Example

```python
hands = extractor.extract_all(frame)

if len(hands) == 2:
    # Both hands visible - make two-digit number
    left_hand = next((h for h in hands if h["label"] == "Left"), None)
    right_hand = next((h for h in hands if h["label"] == "Right"), None)
    
    if left_hand and right_hand:
        # Left hand = tens digit
        left_landmarks = left_hand["landmarks"]
        tens_digit = model.predict(left_landmarks.reshape(1, -1))[0]
        
        # Right hand = ones digit
        right_landmarks = right_hand["landmarks"]
        ones_digit = model.predict(right_landmarks.reshape(1, -1))[0]
        
        # Combine into two-digit number
        two_digit_number = tens_digit * 10 + ones_digit
        print(f"Number: {two_digit_number} ({tens_digit}{ones_digit})")
elif len(hands) == 1:
    # Single hand - treat as single digit
    landmarks = hands[0]["landmarks"]
    digit = model.predict(landmarks.reshape(1, -1))[0]
    print(f"Number: {digit}")
else:
    # No hands
    print("No hands detected")
```

---

## Pattern 9: Fallback Chain (Graceful Degradation)

### Use Case
- Try preferred hand, fall back if not available
- Ensure continuous detection
- Graceful handling of hand appearance/disappearance

### Code Example

```python
# Preference order: Right → Left → Any
preferred_order = ["Right", "Left"]

def get_active_hand(hands, preference_order):
    """Get hand following preference order, or first available."""
    # Try preferred hands first
    for pref in preference_order:
        for hand in hands:
            if hand["label"] == pref:
                return hand
    
    # Fallback: return first hand
    return hands[0] if hands else None

hands = extractor.extract_all(frame)
active_hand = get_active_hand(hands, preferred_order)

if active_hand:
    landmarks = active_hand["landmarks"]
    digit = model.predict(landmarks.reshape(1, -1))[0]
    print(f"Active hand ({active_hand['label']}): {digit}")
else:
    print("No hands detected")
```

---

## Pattern 10: Performance Optimization

### Use Case
- Process only one hand to improve FPS
- Selective processing based on hand availability
- Real-time performance critical

### Code Example

```python
import time

start_time = time.perf_counter()

hands = extractor.extract_all(frame)

# Process only if FPS is critical
process_both = True  # Set to False if FPS drops below threshold

if process_both or len(hands) <= 1:
    # Process all hands (or just one if only one present)
    for hand in hands:
        landmarks = hand["landmarks"]
        digit = model.predict(landmarks.reshape(1, -1))[0]
else:
    # Single hand - process preferred
    right_hand = next((h for h in hands if h["label"] == "Right"), None)
    if right_hand:
        landmarks = right_hand["landmarks"]
        digit = model.predict(landmarks.reshape(1, -1))[0]

elapsed = time.perf_counter() - start_time
fps = 1.0 / elapsed
print(f"FPS: {fps:.1f}")

# Adjust processing based on FPS
if fps < 15:  # Too slow
    process_both = False
```

---

## Common Mistakes & Solutions

### ❌ Mistake 1: Assuming Hand Order

```python
# WRONG: Assumes first hand is right
right_hand = hands[0]

# CORRECT: Check the label
right_hands = [h for h in hands if h["label"] == "Right"]
if right_hands:
    right_hand = right_hands[0]
```

### ❌ Mistake 2: Not Handling Variable Hand Count

```python
# WRONG: Assumes exactly 2 hands
left = hands[0]
right = hands[1]

# CORRECT: Check count first
if len(hands) == 2:
    left = next((h for h in hands if h["label"] == "Left"))
    right = next((h for h in hands if h["label"] == "Right"))
elif len(hands) == 1:
    # Single hand processing
    pass
else:
    # No hands
    pass
```

### ❌ Mistake 3: Using Deprecated Methods

```python
# WRONG: Uses deprecated draw_right_hand()
extractor.draw_right_hand(frame)

# CORRECT: Use new methods
extractor.draw_all_hands(frame)
# OR
extractor.draw_hand_by_index(frame, 0)
```

### ❌ Mistake 4: Not Checking Hand Label

```python
# WRONG: No awareness of hand identity
for hand in hands:
    digit = model.predict(hand["landmarks"].reshape(1, -1))[0]
    print(digit)  # Which hand is this?

# CORRECT: Know which hand you're processing
for hand in hands:
    label = hand["label"]  # Get hand identity
    digit = model.predict(hand["landmarks"].reshape(1, -1))[0]
    print(f"{label}: {digit}")  # Know what you're predicting
```

---

## Testing Patterns

### Test 1: Verify Both Hands are Processed

```python
hands = extractor.extract_all(frame)
assert len(hands) <= 2, "MediaPipe detects max 2 hands"
assert all("label" in h and "landmarks" in h for h in hands), \
    "All hands must have label and landmarks"
print(f"✓ Detected {len(hands)} hands: {[h['label'] for h in hands]}")
```

### Test 2: Verify Equal Accuracy

```python
# Collect predictions for both hands
left_predictions = []
right_predictions = []

for hand in hands:
    prob = model.predict_proba(hand["landmarks"].reshape(1, -1))[0]
    confidence = np.max(prob)
    
    if hand["label"] == "Left":
        left_predictions.append(confidence)
    else:
        right_predictions.append(confidence)

# Compare average confidence
left_avg = np.mean(left_predictions) if left_predictions else 0
right_avg = np.mean(right_predictions) if right_predictions else 0
print(f"Left hand avg confidence: {left_avg:.2%}")
print(f"Right hand avg confidence: {right_avg:.2%}")
```

### Test 3: Verify No Hand Preference

```python
# Test with only left hand visible
left_only_hands = extractor.extract_all(left_only_frame)
assert any(h["label"] == "Left" for h in left_only_hands), \
    "Left hand should be detected when visible"

# Test with only right hand visible
right_only_hands = extractor.extract_all(right_only_frame)
assert any(h["label"] == "Right" for h in right_only_hands), \
    "Right hand should be detected when visible"

print("✓ No hand preference verified")
```

---

## Migration Checklist

Migrating existing code to equal-hand treatment:

- [ ] Replace `extractor.extract(frame)` with `extractor.extract_all(frame)` in main.py
- [ ] Update loop to iterate over all hands returned
- [ ] Add `hand["label"]` checks where hand identity matters
- [ ] Replace `draw_right_hand()` with `draw_all_hands()` or `draw_hand_by_index()`
- [ ] Test with left hand only
- [ ] Test with right hand only
- [ ] Test with both hands
- [ ] Verify predictions are independent for each hand
- [ ] Check per-hand confidence tracking works
- [ ] Verify UI displays both hands when present

---

## Summary

The refactored Sign2Kannada now provides:

✅ **Equal treatment** of left and right hands  
✅ **Flexible patterns** for different use cases  
✅ **Clear semantics** with explicit hand labels  
✅ **Easy migration** from old preference-based approach  
✅ **Better accessibility** for all users  

Choose the pattern that best fits your use case!
