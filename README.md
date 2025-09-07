# E-commerce RPA Scraper & Google Sheets Uploader 
Project Overview
This project is an automated scraping tool designed to extract product data from e-commerce websites. 
It uses Selenium for web scraping, a currency conversion API to normalize prices, 
and gspread to seamlessly upload the data to a Google Sheet.

### Key Features
-	✨ Automated Scraping: Efficiently scrapes product name, price, currency, and rating from a given URL.
-	💸 Price Normalization: Automatically converts scraped prices to a specified target currency, ensuring consistent data.
-	📊 Google Sheets Integration: Uploads all scraped and processed data directly to a Google Sheet for easy access and analysis.
-	⚙️ Customization: Easily adaptable to different websites by updating CSS selectors.

# Getting Started 🚀
### Prerequisites
- ✔️ Python 3.10+
- ✔️ A Google Cloud service account with access to Google Sheets.

### Installation
1.	Clone the repository:
```sh
git clone https://github.com/your-username/your-repo-name.git
```
2. type in `cd your-repo-name`

3.	Create and activate a virtual environment:
```cmd
python -m venv venv
```
4.	source `venv/bin/activate`  # On Windows, use `venv\Scripts\activate`

5.	Install dependencies:
```sh
pip install -r requirements.txt
```

## 🔧 Configuration 
1.	Rename `.env`.example to `.env`.
2.	Update the following variables in the new `.env` file:
```env
	GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/your/service-account.json
	GOOGLE_SHEET_NAME=YourGoogleSheetName
	TARGET_CURRENCY=USD
```

### ▶️ Usage 
Run the script from your terminal and follow the prompts:
`python main.py`

The script will ask for:
- Target URL: The e-commerce listing page to scrape.
- Max Products: The maximum number of products to scrape.
- Target Currency: (Optional) The currency to convert prices to. Press Enter to use the default set in your .env file.
### ⚠️ Important Notes 
- Webdriver Management: The project uses webdriver-manager to automatically handle the installation of the appropriate Selenium driver for Chrome.
- Google Sheets Access: Ensure your service account has editor access to the specified Google Sheet.
- Custom Selectors: The current CSS selectors are generic. For more reliable scraping, it's highly recommended to inspect the target website's HTML and provide custom selectors in the code.

