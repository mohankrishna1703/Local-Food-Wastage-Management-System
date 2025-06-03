import streamlit as st
import pandas as pd
import datetime
import sqlite3

# --- Page Configuration ---
st.set_page_config(
    page_title="Local Food Wastage Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🍽️ Local Food Wastage Management System")
st.write("Welcome to the system for managing surplus food and connecting those in need!")

# --- Database Connection and Data Loading ---
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect('food_wastage.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@st.cache_data(ttl="1h")
def load_data_from_db():
    conn = get_db_connection()
    
    df_food_listings = pd.read_sql_query("SELECT * FROM food_listings", conn)
    df_providers = pd.read_sql_query("SELECT * FROM providers", conn)
    df_receivers = pd.read_sql_query("SELECT * FROM receivers", conn)
    df_claims = pd.read_sql_query("SELECT * FROM claims", conn)

    # Ensure numeric columns are explicitly cast to integer type for consistency
    # Use errors='coerce' to turn any problematic values into NaN, then fill with 0 before converting to int
    df_food_listings['Food_ID'] = pd.to_numeric(df_food_listings['Food_ID'], errors='coerce').fillna(0).astype(int)
    df_food_listings['Provider_ID'] = pd.to_numeric(df_food_listings['Provider_ID'], errors='coerce').fillna(0).astype(int)
    df_food_listings['Quantity'] = pd.to_numeric(df_food_listings['Quantity'], errors='coerce').fillna(0).astype(int)

    df_providers['Provider_ID'] = pd.to_numeric(df_providers['Provider_ID'], errors='coerce').fillna(0).astype(int)
    df_receivers['Receiver_ID'] = pd.to_numeric(df_receivers['Receiver_ID'], errors='coerce').fillna(0).astype(int)
    df_claims['Food_ID'] = pd.to_numeric(df_claims['Food_ID'], errors='coerce').fillna(0).astype(int)
    df_claims['Receiver_ID'] = pd.to_numeric(df_claims['Receiver_ID'], errors='coerce').fillna(0).astype(int)


    df_food_listings['Expiry_Date'] = pd.to_datetime(df_food_listings['Expiry_Date'], errors='coerce')
    df_claims['Timestamp'] = pd.to_datetime(df_claims['Timestamp'], errors='coerce')

    return df_food_listings, df_providers, df_receivers, df_claims

# Load all our dataframes from the database
df_food_listings, df_providers, df_receivers, df_claims = load_data_from_db()


# --- Sidebar Navigation ---
st.sidebar.header("Navigation")
menu_selection = st.sidebar.radio("Go to", ["Key Insights", "Filter Food Listings", "Add New Food Listing", "Manage Food Listings"])

# --- Key Insights Section ---
if menu_selection == "Key Insights":
    st.header("📊 Key Insights from Food Data")

    st.markdown("---")
    st.subheader("1. Providers and Receivers by City")
    providers_city_counts = df_providers['City'].value_counts().reset_index()
    providers_city_counts.columns = ['City', 'Provider Count']
    receivers_city_counts = df_receivers['City'].value_counts().reset_index()
    receivers_city_counts.columns = ['City', 'Receiver Count']

    city_summary = pd.merge(providers_city_counts, receivers_city_counts, on='City', how='outer').fillna(0)
    city_summary['Total Entities'] = city_summary['Provider Count'] + city_summary['Receiver Count']
    city_summary = city_summary.sort_values(by='Total Entities', ascending=False)
    st.dataframe(city_summary)
    st.bar_chart(city_summary.set_index('City')[['Provider Count', 'Receiver Count']])


    st.markdown("---")
    st.subheader("2. Top Food Contributing Provider Types (Total Quantity)")
    provider_type_contribution = df_food_listings.merge(df_providers[['Provider_ID', 'Type']], on='Provider_ID')
    top_provider_types = provider_type_contribution.groupby('Type')['Quantity'].sum().sort_values(ascending=False)
    st.dataframe(top_provider_types)
    st.bar_chart(top_provider_types)

    st.markdown("---")
    st.subheader("3. Contact Information of Providers in a Specific City")
    all_cities = df_providers['City'].unique().tolist()
    all_cities.sort()
    selected_city = st.selectbox("Choose a City:", ['All'] + all_cities)
    if selected_city == 'All':
        st.dataframe(df_providers[['Name', 'Type', 'Address', 'City', 'Contact']])
    else:
        filtered_providers = df_providers[df_providers['City'] == selected_city]
        st.dataframe(filtered_providers[['Name', 'Type', 'Address', 'City', 'Contact']])

    st.markdown("---")
    st.subheader("4. Receivers Who Claimed the Most Food")
    claims_with_food_qty = df_claims.merge(df_food_listings[['Food_ID', 'Quantity']], on='Food_ID')
    receiver_total_claimed = claims_with_food_qty.groupby('Receiver_ID')['Quantity'].sum().reset_index()
    receiver_total_claimed = receiver_total_claimed.merge(df_receivers[['Receiver_ID', 'Name', 'Type']], on='Receiver_ID')
    receiver_total_claimed = receiver_total_claimed.sort_values(by='Quantity', ascending=False).head(10)
    st.dataframe(receiver_total_claimed[['Name', 'Type', 'Quantity']])
    st.bar_chart(receiver_total_claimed.set_index('Name')['Quantity'])

    st.markdown("---")
    st.subheader("5. Total Food Quantity Available (All Listings)")
    total_quantity_available = df_food_listings['Quantity'].sum()
    st.metric("Total Quantity of Food Listed", total_quantity_available)

    st.markdown("---")
    st.subheader("6. City with the Highest Number of Food Listings")
    city_listings_count = df_food_listings['Location'].value_counts().reset_index()
    city_listings_count.columns = ['Location', 'Food_ID_Count']
    city_with_most_listings = city_listings_count.sort_values(by='Food_ID_Count', ascending=False).iloc[0]
    st.write(f"The city/location with the highest number of food listings is **{city_with_most_listings['Location']}** with **{city_with_most_listings['Food_ID_Count']}** listings.")
    st.dataframe(city_listings_count.sort_values(by='Food_ID_Count', ascending=False))
    st.bar_chart(city_listings_count.set_index('Location')['Food_ID_Count'])

    st.markdown("---")
    st.subheader("7. Most Commonly Available Food Types")
    food_type_counts = df_food_listings['Food_Type'].value_counts()
    st.dataframe(food_type_counts)
    st.bar_chart(food_type_counts)

    st.markdown("---")
    st.subheader("8. Number of Claims per Food Item")
    claims_per_food = df_claims.merge(df_food_listings[['Food_ID', 'Food_Name']], on='Food_ID')
    claims_per_food = claims_per_food['Food_ID'].value_counts().reset_index()
    claims_per_food.columns = ['Food_ID', 'Number of Claims']
    claims_per_food = claims_per_food.merge(df_food_listings[['Food_ID', 'Food_Name']], on='Food_ID')
    st.dataframe(claims_per_food.sort_values(by='Number of Claims', ascending=False))

    st.markdown("---")
    st.subheader("9. Provider with Highest Number of Successful Claims")
    successful_claims = df_claims[df_claims['Status'] == 'Completed']
    successful_claims = successful_claims.merge(df_food_listings[['Food_ID', 'Provider_ID']], on='Food_ID')
    provider_successful_claims = successful_claims['Provider_ID'].value_counts().reset_index()
    provider_successful_claims.columns = ['Provider_ID', 'Successful Claims']
    provider_successful_claims = provider_successful_claims.merge(df_providers[['Provider_ID', 'Name', 'Type']], on='Provider_ID')
    top_provider_successful_claims = provider_successful_claims.sort_values(by='Successful Claims', ascending=False).head(1)
    if not top_provider_successful_claims.empty:
        st.write(f"The provider with the highest number of successful claims is **{top_provider_successful_claims['Name'].iloc[0]} ({top_provider_successful_claims['Type'].iloc[0]})** with **{top_provider_successful_claims['Successful Claims'].iloc[0]}** successful claims.")
    else:
        st.write("No successful claims found yet.")
    st.dataframe(provider_successful_claims)


    st.markdown("---")
    st.subheader("10. Percentage of Food Claims by Status")
    claim_status_percentage = df_claims['Status'].value_counts(normalize=True) * 100
    st.dataframe(claim_status_percentage)
    st.bar_chart(claim_status_percentage)

    st.markdown("---")
    st.subheader("11. Average Quantity of Food Claimed Per Receiver")
    receiver_avg_claimed = claims_with_food_qty.groupby('Receiver_ID')['Quantity'].mean().reset_index()
    receiver_avg_claimed = receiver_avg_claimed.merge(df_receivers[['Receiver_ID', 'Name']], on='Receiver_ID')
    st.dataframe(receiver_avg_claimed.sort_values(by='Quantity', ascending=False))

    st.markdown("---")
    st.subheader("12. Most Claimed Meal Type")
    claims_with_meal_type = df_claims.merge(df_food_listings[['Food_ID', 'Meal_Type']], on='Food_ID')
    most_claimed_meal_type = claims_with_meal_type['Meal_Type'].value_counts().reset_index()
    most_claimed_meal_type.columns = ['Meal Type', 'Number of Claims']
    st.dataframe(most_claimed_meal_type)
    st.bar_chart(most_claimed_meal_type.set_index('Meal Type'))

    st.markdown("---")
    st.subheader("13. Total Quantity of Food Donated by Each Provider")
    provider_donated_qty = df_food_listings.groupby('Provider_ID')['Quantity'].sum().reset_index()
    provider_donated_qty = provider_donated_qty.merge(df_providers[['Provider_ID', 'Name', 'Type']], on='Provider_ID')
    st.dataframe(provider_donated_qty.sort_values(by='Quantity', ascending=False))
    st.bar_chart(provider_donated_qty.set_index('Name')['Quantity'])


    # --- NEW SECTION: ✨ More Key Insights ---
    st.header("✨ More Key Insights")
    st.write("Here are additional insights derived from the food wastage data.")

    st.markdown("---")
    st.subheader("14. Food Items with Quantity Less Than 10")
    low_quantity_food = df_food_listings[df_food_listings['Quantity'] < 10].sort_values(by='Quantity', ascending=True)
    st.dataframe(low_quantity_food[['Food_Name', 'Quantity', 'Expiry_Date', 'Location']])

    st.markdown("---")
    st.subheader("15. Providers with No Claims Against Their Food Listings")
    claimed_food_ids = df_claims['Food_ID'].unique()
    unclaimed_listings = df_food_listings[~df_food_listings['Food_ID'].isin(claimed_food_ids)]
    providers_with_unclaimed_food = unclaimed_listings.merge(df_providers[['Provider_ID', 'Name', 'Type', 'City']], on='Provider_ID')
    unique_providers_with_unclaimed = providers_with_unclaimed_food[['Provider_ID', 'Name', 'Type', 'City']].drop_duplicates()

    if not unique_providers_with_unclaimed.empty:
        st.dataframe(unique_providers_with_unclaimed)
    else:
        st.info("All providers have at least one claimed food listing.")


    st.markdown("---")
    st.subheader("16. Average Quantity of Food Per Provider Type")
    avg_qty_per_provider_type = df_food_listings.merge(df_providers[['Provider_ID', 'Type']], on='Provider_ID')
    avg_qty_per_provider_type = avg_qty_per_provider_type.groupby('Type')['Quantity'].mean().reset_index()
    avg_qty_per_provider_type.columns = ['Provider Type', 'Average Quantity Donated']
    st.dataframe(avg_qty_per_provider_type.sort_values(by='Average Quantity Donated', ascending=False))
    st.bar_chart(avg_qty_per_provider_type.set_index('Provider Type')['Average Quantity Donated'])

    st.markdown("---")
    st.subheader("17. Top 5 Food Items by Total Quantity Listed")
    top_5_food_items_qty = df_food_listings.groupby('Food_Name')['Quantity'].sum().nlargest(5).reset_index()
    top_5_food_items_qty.columns = ['Food Name', 'Total Quantity']
    st.dataframe(top_5_food_items_qty)
    st.bar_chart(top_5_food_items_qty.set_index('Food Name'))

    st.markdown("---")
    st.subheader("18. Claims by Day of the Week")
    df_claims_cleaned = df_claims.dropna(subset=['Timestamp']).copy()
    df_claims_cleaned['Day_of_Week'] = df_claims_cleaned['Timestamp'].dt.day_name()
    claims_by_day = df_claims_cleaned['Day_of_Week'].value_counts().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ], fill_value=0)
    st.dataframe(claims_by_day)
    st.bar_chart(claims_by_day)

    st.markdown("---")
    st.subheader("19. Receivers Who Claimed 'Vegan' Food")
    vegan_food_ids = df_food_listings[df_food_listings['Food_Type'] == 'Vegan']['Food_ID'].unique()
    receivers_of_vegan_food = df_claims[df_claims['Food_ID'].isin(vegan_food_ids)]
    receivers_of_vegan_food = receivers_of_vegan_food.merge(df_receivers[['Receiver_ID', 'Name', 'Type', 'City']], on='Receiver_ID').drop_duplicates(subset=['Receiver_ID'])

    if not receivers_of_vegan_food.empty:
        st.dataframe(receivers_of_vegan_food[['Name', 'Type', 'City']])
    else:
        st.info("No receivers have claimed 'Vegan' food yet.")

    st.markdown("---")
    st.subheader("20. Claimed vs. Listed Food Quantity")
    total_listed_qty = df_food_listings['Quantity'].sum()
    claims_with_food_qty_for_total = df_claims.merge(df_food_listings[['Food_ID', 'Quantity']], on='Food_ID')
    total_claimed_qty = claims_with_food_qty_for_total['Quantity'].sum()
    
    st.write(f"Total Food Listed: **{total_listed_qty}**")
    st.write(f"Total Food Claimed: **{total_claimed_qty}**")

    comparison_df = pd.DataFrame({
        'Category': ['Total Listed', 'Total Claimed'],
        'Quantity': [total_listed_qty, total_claimed_qty]
    })
    st.bar_chart(comparison_df.set_index('Category'))


    st.markdown("---")
    st.subheader("21. Food Listings Expiring in Custom Days")
    days_input = st.number_input("Number of days from today:", min_value=1, value=7, key='expiry_days_input')
    
    custom_expiry_date = datetime.date.today() + datetime.timedelta(days=days_input)
    today_date_for_filter = datetime.date.today()

    expiring_custom_df = df_food_listings[
        (df_food_listings['Expiry_Date'].dt.date >= today_date_for_filter) &
        (df_food_listings['Expiry_Date'].dt.date <= custom_expiry_date)
    ].sort_values(by='Expiry_Date', ascending=True)

    if not expiring_custom_df.empty:
        st.dataframe(expiring_custom_df[['Food_Name', 'Quantity', 'Expiry_Date', 'Location', 'Provider_Type']])
    else:
        st.info(f"No food items are expiring within the next {days_input} days.")

    st.markdown("---")
    st.subheader("22. Distribution of Food Listings by Meal Type")
    meal_type_distribution = df_food_listings['Meal_Type'].value_counts()
    st.dataframe(meal_type_distribution)
    st.bar_chart(meal_type_distribution)

    st.markdown("---")
    st.subheader("23. Highly Active Providers (More than X Listings)")
    min_listings_input = st.number_input("Minimum number of listings:", min_value=1, value=5, key='min_listings_input')

    provider_listings_count = df_food_listings['Provider_ID'].value_counts().reset_index()
    provider_listings_count.columns = ['Provider_ID', 'Number of Listings'] # Correct column name here
    
    # --- FIX START: Corrected column name here ---
    highly_active_providers = provider_listings_count[provider_listings_count['Number of Listings'] >= min_listings_input]
    # --- FIX END ---
    highly_active_providers = highly_active_providers.merge(df_providers[['Provider_ID', 'Name', 'Type', 'City']], on='Provider_ID')

    if not highly_active_providers.empty:
        st.dataframe(highly_active_providers[['Name', 'Type', 'City', 'Number of Listings']].sort_values(by='Number of Listings', ascending=False))
    else:
        st.info(f"No providers found with more than {min_listings_input} listings.")


# --- Filter Food Listings Section ---
elif menu_selection == "Filter Food Listings":
    st.header("🔍 Filter Food Listings")

    col1, col2, col3 = st.columns(3)

    with col1:
        all_locations = ['All'] + df_food_listings['Location'].unique().tolist()
        filter_location = st.selectbox("Filter by Location:", all_locations)

    with col2:
        all_food_types = ['All'] + df_food_listings['Food_Type'].unique().tolist()
        filter_food_type = st.selectbox("Filter by Food Type:", all_food_types)

    with col3:
        all_meal_types = ['All'] + df_food_listings['Meal_Type'].unique().tolist()
        filter_meal_type = st.selectbox("Filter by Meal Type:", all_meal_types)

    filtered_listings_df = df_food_listings.copy()

    if filter_location != 'All':
        filtered_listings_df = filtered_listings_df[filtered_listings_df['Location'] == filter_location]
    if filter_food_type != 'All':
        filtered_listings_df = filtered_listings_df[filtered_listings_df['Food_Type'] == filter_food_type]
    if filter_meal_type != 'All':
        filtered_listings_df = filtered_listings_df[filtered_listings_df['Meal_Type'] == filter_meal_type]

    st.write(f"Displaying {len(filtered_listings_df)} filtered food listings:")
    st.dataframe(filtered_listings_df)


# --- Add New Food Listing Section ---
elif menu_selection == "Add New Food Listing":
    st.header("➕ Add New Food Listing")
    st.write("Use this form to add a new food item to the listings.")

    conn = get_db_connection()
    cursor = conn.cursor()

    with st.form("new_food_listing_form"):
        cursor.execute("SELECT MAX(Food_ID) FROM food_listings;")
        max_food_id = cursor.fetchone()[0]
        new_food_id = (max_food_id or 0) + 1

        food_name = st.text_input("Food Name:", help="e.g., Bread, Fruits, Chicken")
        quantity = st.number_input("Quantity:", min_value=1, value=1, help="Number of units available")
        expiry_date = st.date_input("Expiry Date:", value=datetime.date.today() + datetime.timedelta(days=7), help="When the food expires")

        provider_names = df_providers['Name'].unique().tolist()
        selected_provider_name = st.selectbox("Select Provider:", provider_names)
        
        selected_provider_info = df_providers[df_providers['Name'] == selected_provider_name].iloc[0]
        provider_id = selected_provider_info['Provider_ID']
        provider_type = selected_provider_info['Type']
        location = selected_provider_info['City'] 

        food_type = st.selectbox("Food Type:", ['Vegetarian', 'Non-Vegetarian', 'Vegan'])
        meal_type = st.selectbox("Meal Type:", ['Breakfast', 'Lunch', 'Dinner', 'Snacks'])

        submitted = st.form_submit_button("Add Listing")

        if submitted:
            try:
                insert_query = """
                    INSERT INTO food_listings (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """
                cursor.execute(insert_query, (
                    new_food_id,
                    food_name,
                    quantity,
                    str(expiry_date),
                    provider_id,
                    provider_type,
                    location,
                    food_type,
                    meal_type
                ))
                conn.commit()
                st.success(f"Food listing for '{food_name}' added successfully! (Food ID: {new_food_id})")
                
                load_data_from_db.clear() 
                st.rerun()
            except Exception as e:
                st.error(f"Error adding food listing to database: {e}")


# --- Manage Food Listings (Update & Delete) ---
elif menu_selection == "Manage Food Listings":
    st.header("⚙️ Manage Food Listings")
    st.write("View, update, or delete existing food listings.")

    if not df_food_listings.empty:
        st.subheader("Current Food Listings")
        st.dataframe(df_food_listings[['Food_ID', 'Food_Name', 'Quantity', 'Expiry_Date', 'Location', 'Provider_Type', 'Food_Type', 'Meal_Type']].set_index('Food_ID'))

        if not df_food_listings.empty:
            food_options = df_food_listings.apply(lambda row: f"{row['Food_ID']} - {row['Food_Name']} ({row['Quantity']} units)", axis=1).tolist()
            selected_food_option = st.selectbox("Select a Food Listing to Manage:", [''] + food_options, key='manage_food_select')

            selected_food_id = None
            if selected_food_option:
                selected_food_id = int(selected_food_option.split(' - ')[0])
                selected_listing = df_food_listings[df_food_listings['Food_ID'] == selected_food_id]
                
                if not selected_listing.empty:
                    selected_listing = selected_listing.iloc[0]
                else:
                    st.warning("Selected food listing not found in the current data. Please select another.")
                    selected_food_id = None

            if selected_food_id is not None:
                st.markdown("---")
                st.subheader(f"Manage Listing: {selected_listing['Food_Name']} (ID: {selected_food_id})")

                # --- Update Form ---
                with st.form("update_food_listing_form"):
                    st.write("### Update Details")
                    
                    updated_food_name = st.text_input("Food Name:", value=selected_listing['Food_Name'], key='update_food_name')
                    updated_quantity = st.number_input("Quantity:", min_value=1, value=int(selected_listing['Quantity']), key='update_quantity')
                    
                    current_expiry_date = selected_listing['Expiry_Date'].date() if pd.notna(selected_listing['Expiry_Date']) else datetime.date.today()
                    updated_expiry_date = st.date_input("Expiry Date:", value=current_expiry_date, key='update_expiry_date')

                    provider_name_display = "N/A"
                    matching_providers = df_providers[df_providers['Provider_ID'] == selected_listing['Provider_ID']]
                    if not matching_providers.empty:
                        provider_name_display = f"{matching_providers['Name'].iloc[0]} ({selected_listing['Provider_Type']})"

                    st.text_input("Provider:", value=provider_name_display, disabled=True, key='update_provider')
                    st.text_input("Location:", value=selected_listing['Location'], disabled=True, key='update_location')

                    updated_food_type = st.selectbox("Food Type:", ['Vegetarian', 'Non-Vegetarian', 'Vegan'], index=['Vegetarian', 'Non-Vegetarian', 'Vegan'].index(selected_listing['Food_Type']), key='update_food_type')
                    updated_meal_type = st.selectbox("Meal Type:", ['Breakfast', 'Lunch', 'Dinner', 'Snacks'], index=['Breakfast', 'Lunch', 'Dinner', 'Snacks'].index(selected_listing['Meal_Type']), key='update_meal_type')

                    update_submitted = st.form_submit_button("Update Listing")

                    if update_submitted:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        try:
                            update_query = """
                                UPDATE food_listings
                                SET Food_Name = ?, Quantity = ?, Expiry_Date = ?, Food_Type = ?, Meal_Type = ?
                                WHERE Food_ID = ?;
                            """
                            cursor.execute(update_query, (
                                updated_food_name,
                                updated_quantity,
                                str(updated_expiry_date),
                                updated_food_type,
                                updated_meal_type,
                                selected_food_id
                            ))
                            conn.commit()
                            st.success(f"Listing ID {selected_food_id} updated successfully!")
                            load_data_from_db.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating listing: {e}")

                st.markdown("---")
                # --- Delete Button ---
                st.write("### Delete Listing")
                delete_confirmed = st.button(f"Delete Listing ID {selected_food_id} ({selected_listing['Food_Name']})", help="This action cannot be undone.")
                
                if delete_confirmed:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("SELECT COUNT(*) FROM claims WHERE Food_ID = ?", (selected_food_id,))
                        claims_count = cursor.fetchone()[0]

                        if claims_count > 0:
                            st.warning(f"Cannot delete listing ID {selected_food_id} because there are {claims_count} claims associated with it. Please manage claims first.")
                        else:
                            cursor.execute("DELETE FROM food_listings WHERE Food_ID = ?", (selected_food_id,))
                            conn.commit()
                            st.success(f"Listing ID {selected_food_id} deleted successfully!")
                            load_data_from_db.clear()
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting listing: {e}")
            else:
                st.info("Please select a valid food listing from the dropdown above to manage its details.")
    else:
        st.info("No food listings available to manage. Add some using 'Add New Food Listing' first!")