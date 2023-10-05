import requests
import pandas as pd
import os
import config

# Replace 'YOUR_TOKEN' with your actual API token
token = config.TOKEN

def search_companies(search_word, max_results):
    page_num = 1
    result_count = 0

    # Define the CSV file name
    csv_file = "company_results.csv"

    # Check if the CSV file exists
    if os.path.isfile(csv_file):
        # Read the existing CSV file into a DataFrame
        existing_df = pd.read_csv(csv_file)
    else:
        # Create a new DataFrame if the file does not exist
        existing_df = pd.DataFrame(columns=[
            "企业名称", "联系方式（邮箱）", "联系方式（座机/手机号）", "地址", "网址",
            "注册资本RMB", "企业规模", "参保人数", "从事业务", "业务范畴",
            "年报链接", "经营情况（盈亏/净利润）", "备注"
        ])

    while result_count < max_results:
        # Calculate the number of results to fetch on this page
        page_size = min(20, max_results - result_count)
        
        # Build the API request URL for company search
        search_url = f"http://open.api.tianyancha.com/services/open/search/2.0?word={search_word}&pageSize={page_size}&pageNum={page_num}"
        
        headers = {'Authorization': token}
        
        # Send the API request for company search
        search_response = requests.get(search_url, headers=headers)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            items = search_data.get("result", {}).get("items", [])
            
            # Process each company item on this page
            for item in items:
                # Fetch contact information for this company
                company_id = item.get("id")
                contact_url = f"http://open.api.tianyancha.com/services/open/ic/contact?id={company_id}"
                
                # Send the API request for contact information
                contact_response = requests.get(contact_url, headers=headers)
                
                if contact_response.status_code == 200:
                    contact_data = contact_response.json().get("result", {})
                    
                    # Extract relevant information
                    company_info = {
                        "企业名称": item.get("name"),
                        "联系方式（邮箱）": contact_data.get("email"),
                        "联系方式（座机/手机号）": ";".join([call.get("phoneNumber") for call in contact_data.get("allCalls", [])]),
                        "地址": contact_data.get("regLocation"),
                        "网址": contact_data.get("websiteList"),
                        "注册资本RMB": item.get("regCapital"),
                        "企业规模": item.get("companyType"),
                        "参保人数": "",  # Fill with appropriate value if available
                        "从事业务": "",  # Fill with appropriate value if available
                        "业务范畴": "",  # Fill with appropriate value if available
                        "年报链接": "",  # Fill with appropriate value if available
                        "经营情况（盈亏/净利润）": "",  # Fill with appropriate value if available
                        "备注": ""  # Fill with appropriate value if available
                    }

                    # Append the company information to the DataFrame
                    existing_df = existing_df.append(company_info, ignore_index=True)
                    
                    result_count += 1
        
        # If no more results are available, exit the loop
        if not items:
            break
        
        # Increment the page number for the next request
        page_num += 1

    # Save the combined DataFrame to the CSV file
    existing_df.to_csv(csv_file, index=False)

if __name__ == "__main__":
    search_word = input("Enter the search word (e.g., 上海市 教育企业): ")
    max_results = int(input("Enter the maximum number of results to fetch: "))
    
    search_companies(search_word, max_results)
