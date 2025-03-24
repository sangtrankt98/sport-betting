import os
import matplotlib.pyplot as plt
import logging

def generate_league_visualizations(df, league_name):
    """
    Create performance visualizations for a league
    
    Args:
        df (pd.DataFrame): League standings data
        league_name (str): Name of the league
    """
    logger = logging.getLogger(__name__)
    
    try:
        plt.figure(figsize=(15, 10))
        
        # Points distribution
        plt.subplot(2, 1, 1)
        df.sort_values('points', ascending=False).plot(
            x='team_name', y='points', kind='bar', ax=plt.gca()
        )
        plt.title(f'{league_name} - Team Points')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Goal difference
        plt.subplot(2, 1, 2)
        df['goal_difference'] = df['goals_for'] - df['goals_against']
        df.sort_values('goal_difference', ascending=False).plot(
            x='team_name', y='goal_difference', kind='bar', ax=plt.gca()
        )
        plt.title(f'{league_name} - Goal Difference')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Ensure visualizations directory exists
        os.makedirs('visualizations', exist_ok=True)
        
        # Save visualization
        output_path = f'visualizations/{league_name.lower().replace(" ", "_")}_analysis.png'
        plt.savefig(output_path)
        plt.close()
        
        logger.info(f"Visualization created for {league_name}")
    
    except Exception as e:
        logger.error(f"Visualization error for {league_name}: {e}")