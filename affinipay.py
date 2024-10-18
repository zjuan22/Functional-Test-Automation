from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Define the base URL
BASE_URL = "https://automation-sandbox-python-mpywqjbdza-uc.a.run.app"

# Set up driver
def setup_browser():
    driver = webdriver.Firefox()
    driver.get(BASE_URL)
    driver.maximize_window()
    return driver

# Utility function for login
def login(driver, username, password):
    driver.get(BASE_URL)
    
    # Wait until the username field is present using the name attribute
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    # Clear and send username
    driver.find_element(By.NAME, "username").clear()
    driver.find_element(By.NAME, "username").send_keys(username)
    
    # Clear and send password
    driver.find_element(By.NAME, "password").clear()
    driver.find_element(By.NAME, "password").send_keys(password)
    
    driver.find_element(By.ID, "btnLogin").click()

# Utility function for logout
def logout(driver):
    try:
        logout_button = driver.find_element(By.LINK_TEXT, "Logout")
        logout_button.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
            )
        print(f"Logout successful")
    except Exception as e:
        print(f"Failed to log out. Error: {e}")

# Test case TC001 - Positive login validation
def test_login_valid(driver):
    login(driver, "demouser", "abc123")
    time.sleep(2)  # Wait for redirection
    assert "Invoice List" in driver.page_source, "Login failed. Invoice List page not found."
    print("TC001 - Login passed")
    logout(driver)

# Test case TC002 - Negative login validation
def test_login_invalid(driver):
    invalid_credentials = [
        ("Demouser", "abc123"),
        ("demouser_", "abc123"),
        ("demouser", "nananana"),
        ("demouser", "abc123")
    ]
    
    for username, password in invalid_credentials:
        driver.get(BASE_URL)
        
        # Wait until the 'username' field is present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        
        # Execute the login function
        login(driver, username, password)
        
        time.sleep(2)  # Wait for redirection
        
        try:
            # Try to locate the error message if login fails
            error_message = driver.find_element(By.CLASS_NAME, "alert-danger").text
            assert "Wrong username or password." in error_message, f"Failed for {username}, {password}"
            print(f"TC002 - Negative login passed for {username}, {password}")
        
        except:
            # Check if login was successful by verifying the current URL
            current_url = driver.current_url
            if "account" in current_url:
                print(f"TC002 - Negative login failed for {username}, {password}")
                # Perform logout if login was successful
                logout(driver)
            
            else:
                print(f"Unable to locate element: .alert-danger for {username}, {password}")

# Test case TC003 - Validate invoice details
def test_validate_invoice_details(driver):
    driver.get(BASE_URL)
    login(driver, "demouser", "abc123")
    time.sleep(2)  # Wait for redirection
    
    # Find and click the "Invoice Details" link to open a new window
    invoice_link = driver.find_element(By.LINK_TEXT, "Invoice Details")
    invoice_link.click()

    time.sleep(2)  # Wait for redirection
    
    # Switch control to the new window
    original_window = driver.current_window_handle
    WebDriverWait(driver, 10).until(EC.new_window_is_opened)
    new_window = [window for window in driver.window_handles if window != original_window][0]
    driver.switch_to.window(new_window)
    
    # Verify the new window contains the correct details
    expected_data = {
        "Hotel Name": "Rendezvous Hotel",
        "Invoice Number": "110",
        "Invoice Date": "14/01/2018",
        "Due Date": "15/01/2018",
        "Booking Code": "0875",
        "Room": "Superior Double",
        "Total Stay Count": "1",
        "Total Stay Amount": "$150",
        "Check-In": "14/01/2018",
        "Check-Out": "15/01/2018",
        "Customer Details": "JOHNY SMITH\nR2, AVENUE DU MAROC\n123456",
        "Deposit Now": "USD $20.90",
        "Tax&VAT": "USD $19",
        "Total Amount": "USD $209"
    }

    # Wait until the hotel title is visible
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.TAG_NAME, "h4")))
    
    # Validation of the invoice page data
    assert driver.find_element(By.TAG_NAME, "h4").text == expected_data["Hotel Name"]
    assert "Invoice #110 details" in driver.find_element(By.TAG_NAME, "h6").text
    assert driver.find_element(By.XPATH, "//li[span[text()='Invoice Date:']]").text == f"Invoice Date: {expected_data['Invoice Date']}"
    assert driver.find_element(By.XPATH, "//li[span[text()='Due Date:']]").text == f"Due Date: {expected_data['Due Date']}"
    assert driver.find_element(By.XPATH, "//td[text()='Booking Code']/following-sibling::td").text == expected_data["Booking Code"]
    assert driver.find_element(By.XPATH, "//td[text()='Room']/following-sibling::td").text == expected_data["Room"]
    assert driver.find_element(By.XPATH, "//td[text()='Total Stay Count']/following-sibling::td").text == expected_data["Total Stay Count"]
    assert driver.find_element(By.XPATH, "//td[text()='Total Stay Amount']/following-sibling::td").text == expected_data["Total Stay Amount"]
    assert driver.find_element(By.XPATH, "//td[text()='Check-In']/following-sibling::td").text == expected_data["Check-In"]
    assert driver.find_element(By.XPATH, "//td[text()='Check-Out']/following-sibling::td").text == expected_data["Check-Out"]
    
    # Verify 'Customer Details' value
    cust_details_value = driver.find_element(By.XPATH, "//h5[text()='Customer Details']/following-sibling::div").text
    assert cust_details_value.strip() == expected_data["Customer Details"], f"Expected Customer Details: {expected_data['Customer Details']}, but got {cust_details_value.strip()}"

    # Verify 'Deposit Now' value
    deposit_now_value = driver.find_element(By.XPATH, "//h5[text()='Billing Details']/following-sibling::table/tbody/tr/td[1]").text
    assert deposit_now_value == expected_data["Deposit Now"], f"Expected Deposit Now: {expected_data['Deposit Now']}, but got {deposit_now_value}"

    # Verify 'Tax&VAT' value
    tax_vat_value = driver.find_element(By.XPATH, "//h5[text()='Billing Details']/following-sibling::table/tbody/tr/td[2]").text
    assert tax_vat_value == expected_data["Tax&VAT"], f"Expected Tax&VAT: {expected_data['Tax&VAT']}, but got {tax_vat_value}"

    # Verify 'Total Amount' value
    total_amount_value = driver.find_element(By.XPATH, "//h5[text()='Billing Details']/following-sibling::table/tbody/tr/td[3]").text
    assert total_amount_value == expected_data["Total Amount"], f"Expected Total Amount: {expected_data['Total Amount']}, but got {total_amount_value}"

    print("TC003 - Invoice details validation passed")
    
    # Close the new window and switch back to the original window
    driver.close()
    driver.switch_to.window(original_window)

# Main script to run the test cases
if __name__ == "__main__":
    driver = setup_browser()
    try:
        test_login_valid(driver)
        test_login_invalid(driver)
        test_validate_invoice_details(driver)
    finally:
        driver.quit()
