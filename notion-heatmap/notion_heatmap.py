import requests
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta


NOTION_SECRET = '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'  # or use os.environ['NOTION_SECRET']
DATABASE_ID = '20ba6b2eb1ea80e89ecce8e9c5a3a447'      # or use os.environ['DATABASE_ID']

# 1. Fetch data from Notion API - pseudo function
# def fetch_notion_data():
#     url = "https://api.notion.com/v1/databases/{}/query".format(DATABASE_ID)
#     headers = {
#         "Authorization": f"Bearer {NOTION_SECRET}",
#         "Notion-Version": "2022-06-28",
#         "Content-Type": "application/json"
#     }

#     has_more = True
#     next_cursor = None
#     results = []

#     while has_more:
#         payload = {}
#         if next_cursor:
#             payload["start_cursor"] = next_cursor

#         response = requests.post(url, headers=headers, json=payload)
#         data = response.json()

#         for page in data["results"]:
#             try:
#                 # Adjust property names if needed
#                 date = page["properties"]["Date"]["date"]["start"]
#                 checked = page["properties"]["Task"]["checkbox"]
#                 results.append({"date": date, "checked": checked})
#             except KeyError:
#                 continue  # Skip pages with missing data

#         has_more = data.get("has_more", False)
#         next_cursor = data.get("next_cursor", None)

#     return results

# # 2. Process Data
# data = fetch_notion_data()
# df = pd.DataFrame(data)
# df['week'] = df['date'].dt.isocalendar().week
# df['weekday'] = df['date'].dt.weekday  # Monday=0, Sunday=6
# df['year'] = df['date'].dt.year


# # Aggregate by month
# progress = df.groupby(['year', 'month'])['checked'].mean().reset_index()
# progress['progress_percent'] = progress['checked'] * 100

# # 3. Pivot for heatmap matrix: years x months
# heatmap_data = progress.pivot(index='year', columns='month', values='progress_percent')
# import calendar
# heatmap_data.columns = [calendar.month_abbr[m] for m in heatmap_data.columns]


# # 4. Plot heatmap
# plt.figure(figsize=(12, 6))
# sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={'label': 'Progress %'})
# plt.title('Monthly User Progress Heatmap')
# plt.xlabel('Month')
# plt.ylabel('Year')
# plt.show()


# 1. Fetch Data from Notion
def fetch_notion_data():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_SECRET}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    has_more = True
    next_cursor = None
    results = []

    while has_more:
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        for page in data["results"]:
            try:
                date = page["properties"]["Date"]["date"]["start"]
                checked = page["properties"]["Task"]["checkbox"]
                results.append({"date": date, "checked": int(checked)})
            except KeyError:
                continue

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor", None)

    return results

# 2. Prepare Data
data = fetch_notion_data()
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

# Fill missing days
start = df['date'].min()
end = df['date'].max()
all_days = pd.date_range(start=start, end=end, freq='D')
df_full = pd.DataFrame({'date': all_days})
df = pd.merge(df_full, df, on='date', how='left')
df['checked'] = df['checked'].fillna(0)

# 3. Pivot for heatmap-like layout (7 rows for weekdays)
df['dow'] = df['date'].dt.weekday  # 0 = Mon
df['week'] = ((df['date'] - start).dt.days // 7)

z = df.pivot(index='dow', columns='week', values='checked').values

# 4. Labels
text = df.pivot(index='dow', columns='week', values='date').values
# hovertext = [[d.strftime('%A, %b %d, %Y') if pd.notna(d) else '' for d in row] for row in text]
hovertext = [[pd.Timestamp(d).strftime('%A, %b %d, %Y') if pd.notna(d) else '' for d in row] for row in text]

# 5. Plot with Plotly
fig = go.Figure(data=go.Heatmap(
    z=z,
    text=hovertext,
    hoverinfo="text",
    xgap=2,
    ygap=2,
    colorscale='Blues',
    showscale=True,
    colorbar=dict(title='Completed')
))

fig.update_layout(
    title='Daily Task Completion Heatmap (GitHub Style)',
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(
        tickmode='array',
        tickvals=list(range(7)),
        ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    ),
    height=250,
    margin=dict(t=40, b=20, l=20, r=20)
)

fig.show()
# fig.write_image("heatmap.png")