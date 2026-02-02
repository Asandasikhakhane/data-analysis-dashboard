import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Interactive Data Dashboard with Downloads")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Data Preview")
    st.write(df.head())

    st.subheader("Data Summary")
    st.write(df.describe())

    # --- Sidebar Filters ---
    st.sidebar.header("🔎 Filters")
    columns = df.columns.tolist()
    filtered_df = df.copy()

    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            min_val = float(df[col].min())
            max_val = float(df[col].max())
            selected_range = st.sidebar.slider(
                f"{col} range",
                min_val, max_val, (min_val, max_val)
            )
            filtered_df = filtered_df[
                (filtered_df[col] >= selected_range[0]) &
                (filtered_df[col] <= selected_range[1])
            ]
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_datetime(df[col], errors="coerce")
            min_date = df[col].min()
            max_date = df[col].max()
            selected_date = st.sidebar.date_input(
                f"{col} date range",
                (min_date, max_date)
            )
            if isinstance(selected_date, tuple) and len(selected_date) == 2:
                filtered_df = filtered_df[
                    (filtered_df[col] >= pd.to_datetime(selected_date[0])) &
                    (filtered_df[col] <= pd.to_datetime(selected_date[1]))
                ]
        else:
            unique_values = df[col].dropna().unique()
            selected_values = st.sidebar.multiselect(f"{col}", unique_values)
            if selected_values:
                filtered_df = filtered_df[filtered_df[col].isin(selected_values)]

    st.subheader("Filtered Data")
    st.write(filtered_df)

    # --- Download Filtered Data ---
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_data.csv",
        mime="text/csv"
    )

    # --- Plot Controls in Sidebar ---
    st.sidebar.header("📈 Plot Controls")
    x_column = st.sidebar.selectbox("Select x-axis column", columns)
    y_column = st.sidebar.selectbox("Select y-axis column", columns)
    chart_type = st.sidebar.selectbox(
        "Select chart type",
        ["Line", "Bar", "Scatter", "Histogram", "Box", "Pie"]
    )

    if st.sidebar.button("Generate Plot"):
        try:
            if chart_type == "Line":
                fig = px.line(filtered_df, x=x_column, y=y_column, title="Line Chart")
            elif chart_type == "Bar":
                fig = px.bar(filtered_df, x=x_column, y=y_column, title="Bar Chart")
            elif chart_type == "Scatter":
                fig = px.scatter(filtered_df, x=x_column, y=y_column, title="Scatter Plot")
            elif chart_type == "Histogram":
                fig = px.histogram(filtered_df, x=y_column, title="Histogram")
            elif chart_type == "Box":
                fig = px.box(filtered_df, y=y_column, title="Box Plot")
            elif chart_type == "Pie":
                fig = px.pie(filtered_df, names=x_column, values=y_column, title="Pie Chart")

            st.plotly_chart(fig, use_container_width=True)

            # --- Download Plot Options ---
            # Save as HTML (interactive)
            html_bytes = fig.to_html().encode("utf-8")
            st.download_button(
                label="⬇️ Download Plot as HTML (interactive)",
                data=html_bytes,
                file_name="plot.html",
                mime="text/html"
            )

            # Save as PNG (static image)
            png_bytes = fig.to_image(format="png")
            st.download_button(
                label="⬇️ Download Plot as PNG (image)",
                data=png_bytes,
                file_name="plot.png",
                mime="image/png"
            )

        except Exception as e:
            st.error(f"Could not generate plot: {e}")
else:
    st.write("Waiting on file upload....")