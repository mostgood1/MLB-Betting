"""
Prediction Engine Performance Dashboard
=====================================

A comprehensive dashboard for monitoring prediction engine performance,
tracking tuning history, and visualizing key metrics.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import numpy as np
from dataclasses import asdict
import logging

logger = logging.getLogger(__name__)

class PerformanceDashboard:
    """Interactive dashboard for monitoring prediction engine performance"""
    
    def __init__(self, data_dir: str = "MLB-Betting/data"):
        self.data_dir = data_dir
        self.performance_history = []
        self.tuning_history = []
        self.current_metrics = {}
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        sns.set_palette("husl")
    
    def load_performance_data(self) -> bool:
        """Load historical performance data"""
        try:
            # Load performance tracking file
            perf_file = os.path.join(self.data_dir, 'performance_history.json')
            if os.path.exists(perf_file):
                with open(perf_file, 'r') as f:
                    self.performance_history = json.load(f)
            
            # Load tuning history
            tuning_file = os.path.join(self.data_dir, 'tuning_history.json')
            if os.path.exists(tuning_file):
                with open(tuning_file, 'r') as f:
                    self.tuning_history = json.load(f)
            
            logger.info(f"Loaded {len(self.performance_history)} performance records")
            return True
            
        except Exception as e:
            logger.error(f"Error loading performance data: {e}")
            return False
    
    def add_performance_record(self, metrics: Dict[str, Any]) -> None:
        """Add new performance record"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            **metrics
        }
        
        self.performance_history.append(record)
        self._save_performance_data()
    
    def _save_performance_data(self) -> None:
        """Save performance data to file"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            
            perf_file = os.path.join(self.data_dir, 'performance_history.json')
            with open(perf_file, 'w') as f:
                json.dump(self.performance_history, f, indent=2)
            
            tuning_file = os.path.join(self.data_dir, 'tuning_history.json')
            with open(tuning_file, 'w') as f:
                json.dump(self.tuning_history, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving performance data: {e}")
    
    def generate_performance_plots(self) -> List[str]:
        """Generate comprehensive performance visualization plots"""
        if not self.performance_history:
            logger.warning("No performance data available for plotting")
            return []
        
        plot_files = []
        
        try:
            # Convert to DataFrame for easier plotting
            df = pd.DataFrame(self.performance_history)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Create plots directory
            plots_dir = "MLB-Betting/plots"
            os.makedirs(plots_dir, exist_ok=True)
            
            # 1. Score Accuracy Over Time
            plt.figure(figsize=(12, 6))
            plt.subplot(2, 2, 1)
            if 'score_mae' in df.columns:
                plt.plot(df['timestamp'], df['score_mae'], marker='o', linewidth=2)
                plt.title('Score Prediction Accuracy (MAE)')
                plt.ylabel('Mean Absolute Error')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
            
            # 2. Win Probability Accuracy
            plt.subplot(2, 2, 2)
            if 'win_accuracy' in df.columns:
                plt.plot(df['timestamp'], df['win_accuracy'], marker='s', color='green', linewidth=2)
                plt.title('Win Probability Accuracy')
                plt.ylabel('Accuracy Rate')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
            
            # 3. Betting ROI Trend
            plt.subplot(2, 2, 3)
            if 'betting_roi' in df.columns:
                plt.plot(df['timestamp'], df['betting_roi'], marker='^', color='orange', linewidth=2)
                plt.title('Betting ROI Trend')
                plt.ylabel('ROI Percentage')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
            
            # 4. Overall Performance Grade
            plt.subplot(2, 2, 4)
            if 'overall_grade' in df.columns:
                grade_map = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0}
                grades = [grade_map.get(g[0] if g else 'C', 2) for g in df['overall_grade']]
                plt.plot(df['timestamp'], grades, marker='d', color='purple', linewidth=2)
                plt.title('Overall Performance Grade')
                plt.ylabel('Grade (A=4, B=3, C=2, D=1, F=0)')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            plot_file = os.path.join(plots_dir, f"performance_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            plot_files.append(plot_file)
            
            # 5. Parameter Evolution Heatmap
            self._create_parameter_heatmap(plots_dir, plot_files)
            
            # 6. ROI Distribution Analysis
            self._create_roi_analysis(df, plots_dir, plot_files)
            
            logger.info(f"Generated {len(plot_files)} performance plots")
            return plot_files
            
        except Exception as e:
            logger.error(f"Error generating plots: {e}")
            return []
    
    def _create_parameter_heatmap(self, plots_dir: str, plot_files: List[str]) -> None:
        """Create heatmap showing parameter evolution over time"""
        try:
            if not self.tuning_history:
                return
            
            # Extract parameter changes
            param_data = []
            for record in self.tuning_history:
                if 'parameter_changes' in record:
                    param_data.append({
                        'timestamp': record['timestamp'],
                        **record['parameter_changes']
                    })
            
            if not param_data:
                return
            
            df = pd.DataFrame(param_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Create heatmap of parameter values over time
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                plt.figure(figsize=(12, 8))
                
                # Normalize data for better visualization
                normalized_data = df[numeric_cols].apply(lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else x)
                
                sns.heatmap(normalized_data.T, 
                           xticklabels=df['timestamp'].dt.strftime('%m-%d'),
                           cmap='RdYlBu_r', 
                           center=0.5,
                           annot=True, 
                           fmt='.2f')
                
                plt.title('Parameter Evolution Heatmap')
                plt.xlabel('Time')
                plt.ylabel('Parameters')
                plt.xticks(rotation=45)
                
                plot_file = os.path.join(plots_dir, f"parameter_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                plt.savefig(plot_file, dpi=300, bbox_inches='tight')
                plt.close()
                plot_files.append(plot_file)
                
        except Exception as e:
            logger.error(f"Error creating parameter heatmap: {e}")
    
    def _create_roi_analysis(self, df: pd.DataFrame, plots_dir: str, plot_files: List[str]) -> None:
        """Create detailed ROI analysis plots"""
        try:
            if 'betting_roi' not in df.columns:
                return
            
            plt.figure(figsize=(15, 10))
            
            # 1. ROI Distribution
            plt.subplot(2, 3, 1)
            plt.hist(df['betting_roi'].dropna(), bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            plt.title('ROI Distribution')
            plt.xlabel('ROI Percentage')
            plt.ylabel('Frequency')
            plt.grid(True, alpha=0.3)
            
            # 2. ROI vs Score Accuracy
            plt.subplot(2, 3, 2)
            if 'score_mae' in df.columns:
                plt.scatter(df['score_mae'], df['betting_roi'], alpha=0.6, color='orange')
                plt.title('ROI vs Score Accuracy')
                plt.xlabel('Score MAE')
                plt.ylabel('ROI Percentage')
                plt.grid(True, alpha=0.3)
            
            # 3. ROI vs Win Accuracy
            plt.subplot(2, 3, 3)
            if 'win_accuracy' in df.columns:
                plt.scatter(df['win_accuracy'], df['betting_roi'], alpha=0.6, color='green')
                plt.title('ROI vs Win Accuracy')
                plt.xlabel('Win Accuracy')
                plt.ylabel('ROI Percentage')
                plt.grid(True, alpha=0.3)
            
            # 4. Rolling Average ROI
            plt.subplot(2, 3, 4)
            rolling_roi = df['betting_roi'].rolling(window=7, min_periods=1).mean()
            plt.plot(df['timestamp'], rolling_roi, linewidth=3, color='red')
            plt.title('7-Day Rolling Average ROI')
            plt.xlabel('Time')
            plt.ylabel('ROI Percentage')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # 5. Performance Consistency
            plt.subplot(2, 3, 5)
            roi_std = df['betting_roi'].rolling(window=7, min_periods=1).std()
            plt.plot(df['timestamp'], roi_std, linewidth=2, color='purple')
            plt.title('ROI Volatility (7-day std)')
            plt.xlabel('Time')
            plt.ylabel('ROI Standard Deviation')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # 6. Cumulative ROI
            plt.subplot(2, 3, 6)
            cumulative_roi = df['betting_roi'].cumsum()
            plt.plot(df['timestamp'], cumulative_roi, linewidth=3, color='darkgreen')
            plt.title('Cumulative ROI')
            plt.xlabel('Time')
            plt.ylabel('Cumulative ROI')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            plot_file = os.path.join(plots_dir, f"roi_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            plot_files.append(plot_file)
            
        except Exception as e:
            logger.error(f"Error creating ROI analysis: {e}")
    
    def generate_dashboard_html(self) -> str:
        """Generate HTML dashboard with embedded plots and metrics"""
        try:
            # Generate plots first
            plot_files = self.generate_performance_plots()
            
            # Calculate current metrics
            current_metrics = self._calculate_current_metrics()
            
            # Create HTML dashboard
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MLB Prediction Engine Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 10px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        .metric-label {{ color: #7f8c8d; font-size: 0.9em; }}
        .plot-container {{ background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .status-good {{ color: #27ae60; }}
        .status-warning {{ color: #f39c12; }}
        .status-poor {{ color: #e74c3c; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 MLB Prediction Engine Dashboard</h1>
        <p>Real-time performance monitoring and analytics</p>
        <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value {self._get_status_class(current_metrics.get('score_mae', 999), 1.5, 2.0, reverse=True)}">{current_metrics.get('score_mae', 'N/A')}</div>
            <div class="metric-label">Score Prediction MAE</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value {self._get_status_class(current_metrics.get('win_accuracy', 0), 0.55, 0.50)}">{current_metrics.get('win_accuracy', 'N/A'):.1%}</div>
            <div class="metric-label">Win Prediction Accuracy</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value {self._get_status_class(current_metrics.get('betting_roi', 0), 3.0, 1.0)}">{current_metrics.get('betting_roi', 'N/A'):.1f}%</div>
            <div class="metric-label">Betting ROI</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value">{current_metrics.get('total_predictions', 'N/A')}</div>
            <div class="metric-label">Total Predictions</div>
        </div>
    </div>
    
    <div class="plot-container">
        <h2>📊 Performance Trends</h2>
        <p>Historical performance metrics showing prediction accuracy and ROI over time.</p>
"""
            
            # Add plot images
            for plot_file in plot_files:
                if os.path.exists(plot_file):
                    # Convert to relative path for HTML
                    rel_path = os.path.relpath(plot_file, 'MLB-Betting')
                    html_content += f'<img src="{rel_path}" style="max-width: 100%; margin: 10px 0;">\n'
            
            html_content += """
    </div>
    
    <div class="plot-container">
        <h2>🔧 Recent Tuning Activity</h2>
"""
            
            # Add tuning history
            recent_tuning = self.tuning_history[-5:] if self.tuning_history else []
            if recent_tuning:
                html_content += "<ul>"
                for record in reversed(recent_tuning):
                    timestamp = record.get('timestamp', 'Unknown')
                    description = record.get('description', 'Tuning performed')
                    html_content += f"<li><strong>{timestamp[:10]}</strong>: {description}</li>"
                html_content += "</ul>"
            else:
                html_content += "<p>No recent tuning activity.</p>"
            
            html_content += """
    </div>
    
    <div class="plot-container">
        <h2>💡 Performance Insights</h2>
"""
            
            # Add insights
            insights = self._generate_insights()
            if insights:
                html_content += "<ul>"
                for insight in insights:
                    html_content += f"<li>{insight}</li>"
                html_content += "</ul>"
            else:
                html_content += "<p>Insufficient data for insights.</p>"
            
            html_content += """
    </div>
    
    <script>
        // Auto-refresh every 5 minutes
        setTimeout(function(){ location.reload(); }, 300000);
    </script>
</body>
</html>
"""
            
            # Save HTML file
            dashboard_file = "MLB-Betting/dashboard.html"
            with open(dashboard_file, 'w') as f:
                f.write(html_content)
            
            logger.info(f"Dashboard generated: {dashboard_file}")
            return dashboard_file
            
        except Exception as e:
            logger.error(f"Error generating dashboard: {e}")
            return ""
    
    def _get_status_class(self, value: float, good_threshold: float, warning_threshold: float, reverse: bool = False) -> str:
        """Get CSS class based on value thresholds"""
        if value == 'N/A':
            return 'status-warning'
        
        try:
            val = float(value)
            if reverse:
                if val <= good_threshold:
                    return 'status-good'
                elif val <= warning_threshold:
                    return 'status-warning'
                else:
                    return 'status-poor'
            else:
                if val >= good_threshold:
                    return 'status-good'
                elif val >= warning_threshold:
                    return 'status-warning'
                else:
                    return 'status-poor'
        except:
            return 'status-warning'
    
    def _calculate_current_metrics(self) -> Dict[str, Any]:
        """Calculate current performance metrics"""
        if not self.performance_history:
            return {}
        
        latest = self.performance_history[-1]
        
        return {
            'score_mae': latest.get('score_mae', 0),
            'win_accuracy': latest.get('win_accuracy', 0),
            'betting_roi': latest.get('betting_roi', 0),
            'total_predictions': latest.get('total_predictions', 0)
        }
    
    def _generate_insights(self) -> List[str]:
        """Generate performance insights"""
        insights = []
        
        if len(self.performance_history) < 2:
            return insights
        
        # Compare recent vs older performance
        recent = self.performance_history[-3:]
        older = self.performance_history[-10:-3] if len(self.performance_history) >= 10 else []
        
        if recent and older:
            recent_avg_roi = np.mean([r.get('betting_roi', 0) for r in recent])
            older_avg_roi = np.mean([r.get('betting_roi', 0) for r in older])
            
            if recent_avg_roi > older_avg_roi + 1:
                insights.append(f"🔥 ROI improving! Recent average: {recent_avg_roi:.1f}% vs previous: {older_avg_roi:.1f}%")
            elif recent_avg_roi < older_avg_roi - 1:
                insights.append(f"⚠️ ROI declining. Recent average: {recent_avg_roi:.1f}% vs previous: {older_avg_roi:.1f}%")
        
        # Check for consistency
        recent_scores = [r.get('score_mae', 0) for r in recent]
        if recent_scores and np.std(recent_scores) < 0.3:
            insights.append("✅ Score predictions showing good consistency")
        
        return insights

def main():
    """Main dashboard execution"""
    print("📊 Generating Performance Dashboard...")
    
    dashboard = PerformanceDashboard()
    
    # Load existing data
    dashboard.load_performance_data()
    
    # Generate dashboard
    dashboard_file = dashboard.generate_dashboard_html()
    
    if dashboard_file:
        print(f"✅ Dashboard generated: {dashboard_file}")
        print("🌐 Open in browser to view real-time metrics")
    else:
        print("❌ Failed to generate dashboard")

if __name__ == "__main__":
    main()
