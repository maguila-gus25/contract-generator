import re

def main():
    file_path = "/Users/gustavoramos/Documents/GitHub/contract-generator/frontend/index.html"
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    loading_js = """
        function toggleLoading(show) {
            let loader = document.getElementById('global-loader');
            if (!loader) {
                loader = document.createElement('div');
                loader.id = 'global-loader';
                loader.innerHTML = '<div style="border: 4px solid #f3f3f3; border-top: 4px solid var(--accent); border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite;"></div><style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>';
                loader.style.position = 'fixed';
                loader.style.top = '0';
                loader.style.left = '0';
                loader.style.width = '100vw';
                loader.style.height = '100vh';
                loader.style.backgroundColor = 'rgba(0,0,0,0.5)';
                loader.style.display = 'flex';
                loader.style.justifyContent = 'center';
                loader.style.alignItems = 'center';
                loader.style.zIndex = '9999';
                document.body.appendChild(loader);
            }
            loader.style.display = show ? 'flex' : 'none';
        }
"""
    
    # Replace the apiCall function in content to use toggleLoading
    # Search for apiCall implementation and add toggleLoading
    old_api_call = """async function apiCall(endpoint, method = 'GET', body = null) {
            const token = getToken();
            const headers = { 'Content-Type': 'application/json' };
            if (token) {
                headers['Authorization'] = 'Bearer ' + token;
            }

            const options = { method, headers };
            if (body) {
                options.body = JSON.stringify(body);
            }

            try {
                // Show loading could be added here
                const res = await fetch(`${API_URL}${endpoint}`, options);"""

    new_api_call = """async function apiCall(endpoint, method = 'GET', body = null) {
            const token = getToken();
            const headers = { 'Content-Type': 'application/json' };
            if (token) {
                headers['Authorization'] = 'Bearer ' + token;
            }

            const options = { method, headers };
            if (body) {
                options.body = JSON.stringify(body);
            }

            toggleLoading(true);
            try {
                const res = await fetch(`${API_URL}${endpoint}`, options);"""

    if old_api_call in content:
        content = content.replace(old_api_call, new_api_call)
        
        # also add toggleLoading(false) in finally
        old_try_catch = """                if (res.status === 204) return null;
                return await res.json();
            } catch (error) {
                alert(error.message);
                throw error;
            }
        }"""
        new_try_catch = """                if (res.status === 204) return null;
                return await res.json();
            } catch (error) {
                alert(error.message);
                throw error;
            } finally {
                toggleLoading(false);
            }
        }"""
        content = content.replace(old_try_catch, new_try_catch)
        
        # Add toggleLoading definition right above apiCall
        content = content.replace("async function apiCall", loading_js + "\n        async function apiCall")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated apiCall with loading indicator.")
    else:
        print("Could not find apiCall function to update.")

if __name__ == "__main__":
    main()
