# 🎯 MLB Prediction Engine Daily Tuning System

This system provides both **manual frontend tuning** and **automated daily optimization** for the MLB prediction engine parameters.

## 🌟 Features

### 🖥️ Frontend Tuning Dashboard
- **Web Interface**: Accessible at `/admin` on your running Flask application
- **Real-time Parameter Adjustment**: Modify all engine parameters through an intuitive UI
- **Live Testing**: Test configuration changes before applying them
- **Performance Metrics**: View current performance and recent trends
- **Configuration Management**: Save, load, and reset configurations

### 🤖 Automated Daily Optimization
- **Scheduled Optimization**: Automatically runs daily at 6:00 AM
- **Performance Analysis**: Analyzes recent game results and betting accuracy
- **Smart Adjustments**: Makes data-driven parameter adjustments
- **Validation**: Evening validation at 11:00 PM to assess improvements
- **Logging**: Comprehensive logs of all optimization activities

## 🚀 Quick Start

### 1. Access the Frontend Dashboard
1. Start your Flask application: `python app.py`
2. Navigate to: `http://localhost:5000/admin`
3. Adjust parameters and test configurations in real-time

### 2. Setup Automated Daily Optimization

#### Windows (Recommended)
```powershell
# Run as Administrator
cd "C:\Users\mostg\OneDrive\Coding\MLBCompare\MLB-Betting"
powershell -ExecutionPolicy Bypass -File setup_daily_optimization.ps1
```

#### Manual Setup
```bash
# Test the optimizer manually
python auto_daily_optimizer.py

# View logs
type data\auto_optimization.log
```

## 📊 Parameter Categories

### ⚾ Pitcher Parameters
- **ERA Weight** (0.0-1.0): Importance of pitcher's earned run average
- **WHIP Weight** (0.0-1.0): Importance of walks + hits per inning pitched
- **Recent Form Weight** (0.0-1.0): Weight given to recent performance
- **Ace/Good Run Impact** (-2.0-0.0): Run adjustment for pitcher quality

### 🏟️ Team Parameters
- **Offensive Runs Weight** (0.0-1.0): Team offensive capability importance
- **Recent Form Weight** (0.0-1.0): Recent team performance weight
- **Home Field Advantage** (0.0-0.5): Home team advantage factor
- **Head-to-Head Weight** (0.0-0.5): Historical matchup importance

### 💰 Betting Parameters
- **High Confidence Threshold** (0.5-1.0): Minimum confidence for high-value bets
- **Medium Confidence Threshold** (0.3-0.8): Medium confidence betting threshold
- **Value Bet Threshold** (0.0-0.2): Minimum edge required for bet recommendations
- **Kelly Multiplier** (0.1-0.5): Kelly criterion bet sizing multiplier

### 🎲 Simulation Parameters
- **Default Simulations** (1000-20000): Standard prediction simulation count
- **Fast Simulations** (500-10000): Quick prediction simulation count
- **Accuracy Simulations** (5000-50000): High-accuracy simulation count

## 📈 Optimization Strategy

### Daily Schedule
- **6:00 AM**: Pre-game optimization using previous day's results
- **11:00 PM**: Evening validation and performance assessment
- **Real-time**: Continuous monitoring for significant performance changes

### Optimization Logic
1. **Performance Analysis**: Evaluate recent winner accuracy, total accuracy, and perfect game percentage
2. **Trend Detection**: Identify improving or declining performance patterns  
3. **Smart Adjustments**: Make incremental parameter changes based on performance gaps
4. **Conservative Approach**: Small, data-driven adjustments to prevent over-optimization

### Automatic Triggers
- Winner accuracy < 55% → Adjust team parameters
- Total accuracy < 45% → Adjust pitcher parameters  
- Perfect games < 15% → Tighten betting parameters
- Declining trend → Increase simulation counts for better accuracy

## 🔧 Manual Tuning Guidelines

### Performance Targets
- **Winner Accuracy**: ≥ 55% (industry benchmark: 52-54%)
- **Total Accuracy**: ≥ 45% (industry benchmark: 42-48%)
- **Perfect Games**: ≥ 15% (both winner and total correct)
- **Prediction Speed**: < 100ms average

### Common Adjustments

#### Improving Winner Accuracy
- Increase `offensive_runs_weight` (0.45 → 0.50)
- Increase `recent_form_weight` for teams (0.35 → 0.40)
- Adjust `home_field_advantage` based on recent home/away performance

#### Improving Total Accuracy  
- Increase `era_weight` (0.45 → 0.50)
- Increase pitcher `recent_form_weight` (0.35 → 0.40)
- Fine-tune `ace_run_impact` and `good_run_impact`

#### Optimizing Betting Value
- Adjust `high_confidence_threshold` based on hit rate
- Modify `value_bet_threshold` to balance frequency vs. quality
- Tune `kelly_multiplier` for appropriate bet sizing

## 📁 File Structure

```
MLB-Betting/
├── admin_tuning.py                 # Admin dashboard backend
├── auto_daily_optimizer.py         # Automated optimization engine
├── daily_optimization.bat          # Windows batch scheduler
├── setup_daily_optimization.ps1    # PowerShell setup script
├── templates/admin/
│   └── tuning_dashboard.html       # Frontend dashboard
├── data/
│   ├── optimized_config.json       # Current configuration
│   ├── performance_history.json    # Performance tracking
│   └── auto_optimization.log       # Optimization logs
```

## 🔍 Monitoring & Logs

### Performance Monitoring
- **Real-time Dashboard**: View current performance metrics at `/admin`
- **Historical Data**: Track performance trends over time
- **Configuration History**: See all parameter changes and their impact

### Log Files
- `data/auto_optimization.log`: Automated optimization activities
- `data/daily_optimization.log`: Daily scheduler execution logs
- Console output: Real-time optimization feedback

### Key Metrics to Monitor
- Daily accuracy rates (winner, total, perfect games)
- Parameter change impact over 3-7 day periods
- Betting recommendation success rates
- Prediction engine performance (speed, confidence)

## 🚨 Troubleshooting

### Common Issues

**Admin Dashboard Not Loading**
```bash
# Check Flask app is running with admin blueprint
python app.py
# Navigate to http://localhost:5000/admin
```

**Automated Optimization Not Running**
```powershell
# Check Windows Task Scheduler
# Task: "MLB_Daily_Optimization"
# Manually run: python auto_daily_optimizer.py
```

**Configuration Not Saving**
```bash
# Check file permissions on data/optimized_config.json
# Verify JSON format with: python -c "import json; json.load(open('data/optimized_config.json'))"
```

**Performance Not Improving**
- Allow 3-5 days for parameter changes to show impact
- Check if changes are too small (increase step sizes)
- Verify betting accuracy data is current and complete
- Consider manual fine-tuning for specific edge cases

## 💡 Best Practices

1. **Gradual Changes**: Make small, incremental adjustments (0.05 steps)
2. **Monitor Impact**: Allow 3-7 days to assess parameter change impact
3. **Document Changes**: Use the configuration history to track successful adjustments
4. **Backup Configurations**: Save working configurations before major changes
5. **Performance Baseline**: Establish baseline metrics before optimization
6. **Seasonal Adjustments**: Consider sport seasonality in parameter tuning

## 🔮 Advanced Features

### Custom Optimization Profiles
- Create sport-specific parameter sets
- Save configuration templates for different strategies
- A/B test different parameter combinations

### Integration Opportunities
- **Slack/Discord Notifications**: Daily optimization results
- **Database Integration**: Store performance metrics long-term
- **Machine Learning**: Train optimization models on historical data
- **API Integration**: Real-time parameter adjustment via external systems

---

## 🎯 Summary

This tuning system gives you complete control over your MLB prediction engine:

- **Frontend Dashboard**: Manual, real-time parameter tuning with immediate feedback
- **Automated Optimization**: Daily self-improvement based on actual performance data
- **Comprehensive Monitoring**: Track every aspect of performance and configuration changes
- **Flexible Scheduling**: Customizable optimization timing and validation schedules

The system is designed to continuously improve prediction accuracy while maintaining fast performance and providing actionable betting recommendations.

**Start with the frontend dashboard to understand the parameters, then enable automated optimization for hands-free daily improvements!** 🚀
