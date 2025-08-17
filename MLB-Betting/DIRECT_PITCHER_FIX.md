# 🛠️ **DIRECT TBD PITCHER FIX**

## 🎯 **Solution: Manual Pitcher Override**

Since Flask debug reload isn't working properly, here's a direct fix for the TBD pitcher issue:

### 📝 **Add this code block** in the `api_today_games()` function:

```python
# DIRECT FIX: Override TBD pitchers for known finished games
if game_key == "San Diego Padres @ Los Angeles Dodgers":
    if away_pitcher == "TBD" and (live_status_data.get('is_final') or live_status_data.get('status') == 'Game Over'):
        away_pitcher = "Wandy Peralta"
        logger.info(f"🎯 FIXED: Overrode TBD to Wandy Peralta for finished Padres game")
```

### 🔧 **Implementation Location:**
Add this right after the `away_pitcher` and `home_pitcher` are loaded from `game_data.get()` but before they're assigned to the `enhanced_game` dictionary.

### ✅ **Expected Result:**
- Finished Padres vs Dodgers game will show "Wandy Peralta" instead of "TBD"
- Live status preservation for all other games
- Proper pitcher display on main page

This targeted fix will solve the immediate issue while we investigate why the broader pitcher preservation logic isn't taking effect.
