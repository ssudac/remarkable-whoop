import requests
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime

# Whoop API credentials
whoop_api_key = "93f5e3fc10ae9d096fb30fa68221413b97e2b2f261c3f963cba8013f749c1fe2"
whoop_auth_token = ""  # Get this token from your Whoop account after login

# Remarkable API credentials
remarkable_api_key = "your_remarkable_api_key"
remarkable_api_base_url = "https://api.remarkable.com/"

# Fetch health data from Whoop
response = requests.get(f"https://api.mywhoop.com/v3/users/me/activities?limit=1000", headers={
    "Authorization": f"Bearer {whoop_api_key}",
})
health_data = response.json()

# Parse and process health data
df = pd.DataFrame(health_data)
df['date'] = pd.to_datetime(df['start_time'])

# Extract and store various metrics
heart_rate = df["average_hr"].tolist()
sleep_hours = df["total_sleep_minutes"] / 60
restfulness = df["restfulness_score"].tolist()
calories_burned = df["total_calories_burned"]

# Generate smart suggestions based on sleep data and metrics
suggestions = []
sleep_metrics = df[['date', 'total_sleep_minutes']]
sleep_metrics.columns = ['Date', 'Sleep Hours']
avg_sleep_hours = sleep_metrics['Sleep Hours'].mean()
suggestions.append(f"Average Sleep Hours: {avg_sleep_hours:.1f} hours/night")
if avg_sleep_hours < 7.5:
    suggestions.append("Consider aiming for 7-9 hours of sleep per night to improve overall health.")

# Generate visualizations using Seaborn
sns.set(style="whitegrid")
fig1, ax1 = plt.subplots()
sns.lineplot(x='date', y='average_hr', data=df)
ax1.set_title("Average Heart Rate Trend")
ax1.set(xlabel="Date", ylabel="Average Heart Rate (bpm)")
plt.savefig("heart_rate_trend.png")
plt.close()

fig2, ax2 = plt.subplots()
sns.lineplot(x='date', y=heart_rate, label="Average Heart Rate")
sns.lineplot(x='date', y=restfulness, label="Restfulness Score")
ax2.set_title("Heart Rate and Restfulness Trends")
ax2.legend()
ax2.set(xlabel="Date", ylabel="Value")
plt.savefig("trends.png")
plt.close()

fig3, ax3 = plt.subplots()
sns.lineplot(x='date', y=calories_burned, label="Calories Burned")
ax3.set_title("Calories Burned Trend")
ax3.legend()
ax3.set(xlabel="Date", ylabel="Calories Burned")
plt.savefig("calories_burned.png")
plt.close()

# Format health data, visualizations, and suggestions as markdown files
markdown_content = """
## Comprehensive Health Overview

![Heart Rate and Restfulness Trends](trends.png)

![Calories Burned Trend](calories_burned.png)

## Metrics

| Date       | Average HR (bpm) | Restfulness Score | Calories Burned |
"""
for index, row in df.iterrows():
    markdown_content += f"| {row['date'].strftime('%Y-%m-%d')} | {row['average_hr']} | {row['restfulness_score']} | {int(row['total_calories_burned'])} |\n"

markdown_content += "\n## Smart Suggestions\n"
for suggestion in suggestions:
    markdown_content += f"> {suggestion}\n"

# Upload markdown file and visualizations to Remarkable
with open("health_overview.md", "w") as f:
    f.write(markdown_content)

response = requests.post(remarkable_api_base_url + "files/", headers={
    "Authorization": f"Bearer {remarkable_api_key}",
    "Content-Type": "application/octet-stream",
}, data=open("heart_rate_trend.png", "rb").read())

response = requests.post(remarkable_api_base_url + "files/", headers={
    "Authorization": f"Bearer {remarkable_api_key}",
    "Content-Type": "application/octet-stream",
}, data=open("trends.png", "rb").read())

response = requests.post(remarkable_api_base_url + "files/", headers={
    "Authorization": f"Bearer {remarkable_api_key}",
    "Content-Type": "application/octet-stream",
}, data=open("calories_burned.png", "rb").read())

response = requests.post(remarkable_api_base_url + "files/", headers={
    "Authorization": f"Bearer {remarkable_api_key}",
    "Content-Type": "text/markdown",
}, data=open("health_overview.md".encode(), "rb"))