use tauri::Manager;
use tauri_plugin_shell::ShellExt;
use std::path::Path;

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

/// Check if Chrome is installed on the system
#[tauri::command]
fn check_chrome_installed() -> Result<bool, String> {
    let chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
    Ok(Path::new(chrome_path).exists())
}

/// Launch Chrome with remote debugging enabled
#[tauri::command]
async fn launch_chrome_debug(app: tauri::AppHandle) -> Result<String, String> {
    // First check if Chrome is installed
    if !check_chrome_installed()? {
        return Err("Chrome is not installed. Please install Chrome from https://www.google.com/chrome/".to_string());
    }

    // Get the bundled launch script
    let resource_path = app.path()
        .resource_dir()
        .map_err(|e| format!("Failed to get resource directory: {}", e))?;

    let script_path = resource_path.join("launch-chrome-debug.sh");

    if !script_path.exists() {
        return Err("Chrome launch script not found in app bundle".to_string());
    }

    // Execute the launch script
    let output = std::process::Command::new("bash")
        .arg(&script_path)
        .output()
        .map_err(|e| format!("Failed to execute launch script: {}", e))?;

    if output.status.success() {
        Ok("Chrome launched successfully with remote debugging enabled".to_string())
    } else {
        let error = String::from_utf8_lossy(&output.stderr);
        Err(format!("Failed to launch Chrome: {}", error))
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // Start Python backend as sidecar
            println!("🚀 Starting Python backend sidecar...");

            let sidecar_command = app.shell().sidecar("screenshot-backend")
                .expect("Failed to create sidecar command");

            // Spawn the backend process
            tauri::async_runtime::spawn(async move {
                let (mut rx, _child) = sidecar_command
                    .spawn()
                    .expect("Failed to spawn backend sidecar");

                println!("✅ Backend sidecar started successfully!");

                // Log backend output
                while let Some(event) = rx.recv().await {
                    match event {
                        tauri_plugin_shell::process::CommandEvent::Stdout(line) => {
                            let output = String::from_utf8_lossy(&line);
                            println!("Backend: {}", output.trim());
                        }
                        tauri_plugin_shell::process::CommandEvent::Stderr(line) => {
                            let output = String::from_utf8_lossy(&line);
                            eprintln!("Backend Error: {}", output.trim());
                        }
                        tauri_plugin_shell::process::CommandEvent::Terminated(payload) => {
                            println!("Backend terminated with code: {:?}", payload.code);
                            break;
                        }
                        _ => {}
                    }
                }
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            greet,
            check_chrome_installed,
            launch_chrome_debug
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
