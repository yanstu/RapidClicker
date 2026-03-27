#define WIN32_LEAN_AND_MEAN
#define NOMINMAX

#include <windows.h>
#include <shellapi.h>
#include <shlobj.h>
#include <commctrl.h>
#include <atomic>
#include <string>
#include <deque>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <locale>
#include <codecvt>
#include <vector>
namespace
{
constexpr wchar_t kAppName[] = L"RapidClicker";
constexpr wchar_t kMutexName[] = L"Global\\RapidClicker_Singleton_Lock";
constexpr wchar_t kWindowClassName[] = L"RapidClickerWindowClass";
constexpr wchar_t kSettingsClassName[] = L"RapidClickerSettingsClass";
constexpr wchar_t kAboutClassName[] = L"RapidClickerAboutClass";
constexpr wchar_t kConfigFileName[] = L".rapidclicker.json";
constexpr UINT kTrayIconId = 1001;
constexpr UINT kTrayCallbackMessage = WM_APP + 1;
constexpr UINT kStartAutoClickMessage = WM_APP + 2;
constexpr UINT kStopAutoClickMessage = WM_APP + 3;
constexpr UINT kMenuSettings = 3001;
constexpr UINT kMenuAbout = 3002;
constexpr UINT kMenuExit = 3003;
constexpr wchar_t kAutoStartTaskName[] = L"RapidClicker";
constexpr int kAppIconResourceId = 101;
constexpr int kSettingsIconResourceId = 102;
constexpr int kAboutIconResourceId = 103;
constexpr int kExitIconResourceId = 104;

constexpr int kControlTriggerCount = 4001;
constexpr int kControlTriggerInterval = 4002;
constexpr int kControlAutoClickInterval = 4003;
constexpr int kControlLanguageEn = 4004;
constexpr int kControlLanguageZh = 4005;
constexpr int kControlAutoStart = 4006;
constexpr int kControlSave = 4007;
constexpr int kControlCancel = 4008;

constexpr int kAboutOk = 5001;
constexpr int kGithubLink = 5002;
constexpr int kSettingsInfoText = 4103;
constexpr int kAboutVersionValue = 5106;
constexpr int kAboutAuthorValue = 5107;
constexpr ULONG_PTR kInjectedClickMarker = static_cast<ULONG_PTR>(0x52434C4B);
constexpr DWORD kAutoClickThreadJoinTimeoutMs = 1000;

HFONT g_ui_font = nullptr;
HFONT g_ui_font_bold = nullptr;
HBRUSH g_window_brush = nullptr;
HICON g_menu_icon_settings = nullptr;
HICON g_menu_icon_about = nullptr;
HICON g_menu_icon_exit = nullptr;

struct Config
{
    int trigger_click_count = 5;
    int trigger_click_interval = 300;
    int auto_click_interval = 500;
    bool auto_start = false;
    bool debug_mode = false;
    std::wstring language = L"en";
};

struct Translations
{
    const wchar_t* settings;
    const wchar_t* about;
    const wchar_t* exit_app;
    const wchar_t* settings_title;
    const wchar_t* about_title;
    const wchar_t* mouse_settings;
    const wchar_t* app_settings;
    const wchar_t* trigger_click_count;
    const wchar_t* trigger_click_interval;
    const wchar_t* auto_click_interval;
    const wchar_t* language;
    const wchar_t* english;
    const wchar_t* chinese;
    const wchar_t* auto_start;
    const wchar_t* save;
    const wchar_t* cancel;
    const wchar_t* ok;
    const wchar_t* settings_saved;
    const wchar_t* save_failed;
    const wchar_t* version;
    const wchar_t* author;
    const wchar_t* details;
    const wchar_t* about_description;
    const wchar_t* github;
    const wchar_t* already_running;
};

constexpr Translations kEnglish{
    L"Settings",
    L"About",
    L"Exit",
    L"RapidClicker Settings",
    L"About RapidClicker",
    L"Mouse Settings",
    L"Application Settings",
    L"Trigger Click Count",
    L"Trigger Time Window (ms)",
    L"Auto Click Interval (ms)",
    L"Language",
    L"English",
    L"Chinese",
    L"Auto Start",
    L"Save",
    L"Cancel",
    L"OK",
    L"Settings saved successfully!",
    L"Failed to save settings.",
    L"Version",
    L"Author",
    L"Details",
    L"RapidClicker is a lightweight background auto clicker for Windows.",
    L"GitHub",
    L"RapidClicker is already running.",
};

constexpr Translations kChinese{
    L"\u8bbe\u7f6e",
    L"\u5173\u4e8e",
    L"\u9000\u51fa",
    L"RapidClicker \u8bbe\u7f6e",
    L"\u5173\u4e8e RapidClicker",
    L"\u9f20\u6807\u8bbe\u7f6e",
    L"\u5e94\u7528\u8bbe\u7f6e",
    L"\u89e6\u53d1\u70b9\u51fb\u6b21\u6570",
    L"\u89e6\u53d1\u65f6\u95f4\u7a97\u53e3\uff08\u6beb\u79d2\uff09",
    L"\u81ea\u52a8\u70b9\u51fb\u95f4\u9694\uff08\u6beb\u79d2\uff09",
    L"\u8bed\u8a00",
    L"\u82f1\u6587",
    L"\u4e2d\u6587",
    L"\u5f00\u673a\u81ea\u542f\u52a8",
    L"\u4fdd\u5b58",
    L"\u53d6\u6d88",
    L"\u786e\u5b9a",
    L"\u8bbe\u7f6e\u4fdd\u5b58\u6210\u529f\uff01",
    L"\u4fdd\u5b58\u8bbe\u7f6e\u5931\u8d25\u3002",
    L"\u7248\u672c",
    L"\u4f5c\u8005",
    L"\u8be6\u7ec6\u4fe1\u606f",
    L"RapidClicker \u662f\u4e00\u4e2a\u8f7b\u91cf\u7ea7 Windows \u540e\u53f0\u81ea\u52a8\u8fde\u70b9\u5de5\u5177\u3002",
    L"GitHub",
    L"RapidClicker \u5df2\u5728\u8fd0\u884c\u3002",
};

Config g_config;
HINSTANCE g_instance = nullptr;
HWND g_main_window = nullptr;
HWND g_settings_window = nullptr;
HWND g_about_window = nullptr;
HHOOK g_mouse_hook = nullptr;
HANDLE g_mutex = nullptr;
HANDLE g_auto_click_thread = nullptr;
HANDLE g_auto_click_stop_event = nullptr;
NOTIFYICONDATAW g_notify_icon{};
std::deque<ULONGLONG> g_press_times;
std::atomic<bool> g_button_held{false};
std::atomic<bool> g_auto_clicking{false};
ULONGLONG g_last_press_tick = 0;

const Translations& Tr()
{
    return g_config.language == L"zh" ? kChinese : kEnglish;
}

std::wstring GetExecutablePath()
{
    wchar_t buffer[MAX_PATH];
    GetModuleFileNameW(nullptr, buffer, MAX_PATH);
    return buffer;
}

std::wstring GetDirectoryPath(const std::wstring& file_path)
{
    const size_t pos = file_path.find_last_of(L"\\/");
    if (pos == std::wstring::npos)
    {
        return L".";
    }
    return file_path.substr(0, pos);
}

std::wstring GetConfigPath()
{
    wchar_t profile_path[MAX_PATH];
    if (SUCCEEDED(SHGetFolderPathW(nullptr, CSIDL_PROFILE, nullptr, 0, profile_path)))
    {
        return std::wstring(profile_path) + L"\\" + kConfigFileName;
    }
    return GetDirectoryPath(GetExecutablePath()) + L"\\" + kConfigFileName;
}

std::wstring ReadFileToString(const std::wstring& path)
{
    std::wifstream input(path);
    input.imbue(std::locale(input.getloc(), new std::codecvt_utf8_utf16<wchar_t>));
    if (!input.is_open())
    {
        return L"";
    }
    std::wstringstream buffer;
    buffer << input.rdbuf();
    return buffer.str();
}

bool WriteStringToFile(const std::wstring& path, const std::wstring& content)
{
    std::wofstream output(path, std::ios::trunc);
    output.imbue(std::locale(output.getloc(), new std::codecvt_utf8_utf16<wchar_t>));
    if (!output.is_open())
    {
        return false;
    }
    output << content;
    return output.good();
}

std::wstring JsonEscape(const std::wstring& value)
{
    std::wstring escaped;
    escaped.reserve(value.size());
    for (const wchar_t ch : value)
    {
        if (ch == L'\\' || ch == L'"')
        {
            escaped.push_back(L'\\');
        }
        escaped.push_back(ch);
    }
    return escaped;
}

std::wstring ExtractJsonString(const std::wstring& json, const std::wstring& key, const std::wstring& fallback)
{
    const std::wstring token = L"\"" + key + L"\"";
    size_t pos = json.find(token);
    if (pos == std::wstring::npos)
    {
        return fallback;
    }
    pos = json.find(L':', pos);
    pos = json.find(L'"', pos);
    if (pos == std::wstring::npos)
    {
        return fallback;
    }
    const size_t end = json.find(L'"', pos + 1);
    if (end == std::wstring::npos)
    {
        return fallback;
    }
    return json.substr(pos + 1, end - pos - 1);
}

int ExtractJsonInt(const std::wstring& json, const std::wstring& key, int fallback)
{
    const std::wstring token = L"\"" + key + L"\"";
    size_t pos = json.find(token);
    if (pos == std::wstring::npos)
    {
        return fallback;
    }
    pos = json.find(L':', pos);
    if (pos == std::wstring::npos)
    {
        return fallback;
    }
    ++pos;
    while (pos < json.size() && iswspace(json[pos]))
    {
        ++pos;
    }
    size_t end = pos;
    while (end < json.size() && (iswdigit(json[end]) || json[end] == L'-'))
    {
        ++end;
    }
    if (end == pos)
    {
        return fallback;
    }
    return _wtoi(json.substr(pos, end - pos).c_str());
}

bool ExtractJsonBool(const std::wstring& json, const std::wstring& key, bool fallback)
{
    const std::wstring token = L"\"" + key + L"\"";
    size_t pos = json.find(token);
    if (pos == std::wstring::npos)
    {
        return fallback;
    }
    pos = json.find(L':', pos);
    if (pos == std::wstring::npos)
    {
        return fallback;
    }
    ++pos;
    while (pos < json.size() && iswspace(json[pos]))
    {
        ++pos;
    }
    if (json.compare(pos, 4, L"true") == 0)
    {
        return true;
    }
    if (json.compare(pos, 5, L"false") == 0)
    {
        return false;
    }
    return fallback;
}

void LoadConfig()
{
    const std::wstring json = ReadFileToString(GetConfigPath());
    if (json.empty())
    {
        return;
    }

    g_config.trigger_click_count = std::clamp(ExtractJsonInt(json, L"trigger_click_count", g_config.trigger_click_count), 2, 10);
    g_config.trigger_click_interval = std::clamp(ExtractJsonInt(json, L"trigger_click_interval", g_config.trigger_click_interval), 100, 1000);
    g_config.auto_click_interval = std::clamp(ExtractJsonInt(json, L"auto_click_interval", g_config.auto_click_interval), 10, 500);
    g_config.auto_start = ExtractJsonBool(json, L"auto_start", g_config.auto_start);
    g_config.debug_mode = ExtractJsonBool(json, L"debug_mode", g_config.debug_mode);
    const std::wstring language = ExtractJsonString(json, L"language", g_config.language);
    g_config.language = language == L"zh" ? L"zh" : L"en";
}

bool SetAutoStart(bool enabled)
{
    HKEY run_key = nullptr;
    if (RegOpenKeyExW(
            HKEY_CURRENT_USER,
            L"Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            0,
            KEY_SET_VALUE,
            &run_key) == ERROR_SUCCESS)
    {
        RegDeleteValueW(run_key, kAppName);
        RegCloseKey(run_key);
    }

    wchar_t system_directory[MAX_PATH] = {};
    if (GetSystemDirectoryW(system_directory, MAX_PATH) == 0)
    {
        return false;
    }

    const std::wstring schtasks_path = std::wstring(system_directory) + L"\\schtasks.exe";
    if (GetFileAttributesW(schtasks_path.c_str()) == INVALID_FILE_ATTRIBUTES)
    {
        return false;
    }

    auto quote_argument = [](const std::wstring& value) {
        std::wstring quoted;
        quoted.push_back(L'"');

        unsigned backslash_count = 0;
        for (const wchar_t ch : value)
        {
            if (ch == L'\\')
            {
                ++backslash_count;
                continue;
            }

            if (ch == L'"')
            {
                quoted.append(backslash_count * 2 + 1, L'\\');
                quoted.push_back(L'"');
                backslash_count = 0;
                continue;
            }

            if (backslash_count > 0)
            {
                quoted.append(backslash_count, L'\\');
                backslash_count = 0;
            }
            quoted.push_back(ch);
        }

        if (backslash_count > 0)
        {
            quoted.append(backslash_count * 2, L'\\');
        }

        quoted.push_back(L'"');
        return quoted;
    };

    std::wstring command_line = quote_argument(schtasks_path);
    if (enabled)
    {
        const std::wstring launch_command = L"\"" + GetExecutablePath() + L"\"";
        command_line += L" /Create /SC ONLOGON /TN ";
        command_line += quote_argument(kAutoStartTaskName);
        command_line += L" /TR ";
        command_line += quote_argument(launch_command);
        command_line += L" /RL HIGHEST /F";
    }
    else
    {
        command_line += L" /Delete /TN ";
        command_line += quote_argument(kAutoStartTaskName);
        command_line += L" /F";
    }

    STARTUPINFOW startup_info{};
    startup_info.cb = sizeof(startup_info);
    PROCESS_INFORMATION process_info{};

    std::vector<wchar_t> buffer(command_line.begin(), command_line.end());
    buffer.push_back(L'\0');

    const BOOL created = CreateProcessW(
        nullptr,
        buffer.data(),
        nullptr,
        nullptr,
        FALSE,
        CREATE_NO_WINDOW,
        nullptr,
        nullptr,
        &startup_info,
        &process_info);
    if (!created)
    {
        return false;
    }

    WaitForSingleObject(process_info.hProcess, INFINITE);

    DWORD exit_code = 1;
    GetExitCodeProcess(process_info.hProcess, &exit_code);
    CloseHandle(process_info.hThread);
    CloseHandle(process_info.hProcess);

    if (!enabled && exit_code == 1)
    {
        return true;
    }

    return exit_code == 0;
}

bool SaveConfig()
{
    std::wstringstream json;
    json << L"{\n"
         << L"  \"trigger_click_count\": " << g_config.trigger_click_count << L",\n"
         << L"  \"trigger_click_interval\": " << g_config.trigger_click_interval << L",\n"
         << L"  \"auto_click_interval\": " << g_config.auto_click_interval << L",\n"
         << L"  \"language\": \"" << JsonEscape(g_config.language) << L"\",\n"
         << L"  \"auto_start\": " << (g_config.auto_start ? L"true" : L"false") << L",\n"
         << L"  \"debug_mode\": " << (g_config.debug_mode ? L"true" : L"false") << L"\n"
         << L"}\n";

    const bool file_saved = WriteStringToFile(GetConfigPath(), json.str());
    const bool auto_start_saved = SetAutoStart(g_config.auto_start);
    return file_saved && auto_start_saved;
}

int ScaleForDpi(int value)
{
    const UINT dpi = GetDpiForSystem();
    return MulDiv(value, static_cast<int>(dpi), 96);
}

void EnsureUiResources()
{
    if (!g_window_brush)
    {
        g_window_brush = CreateSolidBrush(RGB(255, 255, 255));
    }

    if (!g_ui_font || !g_ui_font_bold)
    {
        NONCLIENTMETRICSW metrics{};
        metrics.cbSize = sizeof(metrics);
        if (!SystemParametersInfoW(SPI_GETNONCLIENTMETRICS, sizeof(metrics), &metrics, 0))
        {
            ZeroMemory(&metrics, sizeof(metrics));
            metrics.cbSize = sizeof(metrics);
            metrics.lfMessageFont.lfHeight = -ScaleForDpi(9);
            wcscpy_s(metrics.lfMessageFont.lfFaceName, L"Microsoft YaHei UI");
        }

        metrics.lfMessageFont.lfQuality = CLEARTYPE_QUALITY;
        g_ui_font = CreateFontIndirectW(&metrics.lfMessageFont);

        LOGFONTW bold_font = metrics.lfMessageFont;
        bold_font.lfWeight = FW_SEMIBOLD;
        bold_font.lfQuality = CLEARTYPE_QUALITY;
        g_ui_font_bold = CreateFontIndirectW(&bold_font);
    }
}

void ApplyFont(HWND hwnd, HFONT font)
{
    if (hwnd && font)
    {
        SendMessageW(hwnd, WM_SETFONT, reinterpret_cast<WPARAM>(font), TRUE);
    }
}

void ApplyControlFonts(HWND parent)
{
    if (!parent)
    {
        return;
    }

    ApplyFont(GetDlgItem(parent, 4101), g_ui_font_bold);
    ApplyFont(GetDlgItem(parent, 4102), g_ui_font_bold);
    ApplyFont(GetDlgItem(parent, 4201), g_ui_font);
    ApplyFont(GetDlgItem(parent, 4202), g_ui_font);
    ApplyFont(GetDlgItem(parent, 4203), g_ui_font);
    ApplyFont(GetDlgItem(parent, 4204), g_ui_font);
    ApplyFont(GetDlgItem(parent, kControlTriggerCount), g_ui_font);
    ApplyFont(GetDlgItem(parent, kControlTriggerInterval), g_ui_font);
    ApplyFont(GetDlgItem(parent, kControlAutoClickInterval), g_ui_font);
    ApplyFont(GetDlgItem(parent, kControlLanguageEn), g_ui_font);
    ApplyFont(GetDlgItem(parent, kControlLanguageZh), g_ui_font);
    ApplyFont(GetDlgItem(parent, kControlAutoStart), g_ui_font);
    ApplyFont(GetDlgItem(parent, kControlSave), g_ui_font);
    ApplyFont(GetDlgItem(parent, kControlCancel), g_ui_font);
    ApplyFont(GetDlgItem(parent, kSettingsInfoText), g_ui_font);

    ApplyFont(GetDlgItem(parent, 5101), g_ui_font);
    ApplyFont(GetDlgItem(parent, 5102), g_ui_font_bold);
    ApplyFont(GetDlgItem(parent, 5103), g_ui_font);
    ApplyFont(GetDlgItem(parent, 5104), g_ui_font);
    ApplyFont(GetDlgItem(parent, 5105), g_ui_font);
    ApplyFont(GetDlgItem(parent, kAboutVersionValue), g_ui_font);
    ApplyFont(GetDlgItem(parent, kAboutAuthorValue), g_ui_font);
    ApplyFont(GetDlgItem(parent, kGithubLink), g_ui_font);
    ApplyFont(GetDlgItem(parent, kAboutOk), g_ui_font);
}

HICON LoadMenuIcon(int resource_id)
{
    const int icon_size = ScaleForDpi(16);
    return static_cast<HICON>(LoadImageW(
        g_instance,
        MAKEINTRESOURCEW(resource_id),
        IMAGE_ICON,
        icon_size,
        icon_size,
        LR_DEFAULTCOLOR));
}

void EnsureMenuIcons()
{
    if (!g_menu_icon_settings)
    {
        g_menu_icon_settings = LoadMenuIcon(kSettingsIconResourceId);
    }
    if (!g_menu_icon_about)
    {
        g_menu_icon_about = LoadMenuIcon(kAboutIconResourceId);
    }
    if (!g_menu_icon_exit)
    {
        g_menu_icon_exit = LoadMenuIcon(kExitIconResourceId);
    }
}

HICON GetMenuIcon(UINT command_id)
{
    switch (command_id)
    {
    case kMenuSettings:
        return g_menu_icon_settings;
    case kMenuAbout:
        return g_menu_icon_about;
    case kMenuExit:
        return g_menu_icon_exit;
    default:
        return nullptr;
    }
}

RECT GetPreferredWorkArea()
{
    POINT cursor{};
    GetCursorPos(&cursor);
    MONITORINFO monitor_info{};
    monitor_info.cbSize = sizeof(monitor_info);
    const HMONITOR monitor = MonitorFromPoint(cursor, MONITOR_DEFAULTTONEAREST);
    if (monitor && GetMonitorInfoW(monitor, &monitor_info))
    {
        return monitor_info.rcWork;
    }

    RECT work_area{};
    SystemParametersInfoW(SPI_GETWORKAREA, 0, &work_area, 0);
    return work_area;
}

RECT AdjustWindowRectForClient(int client_width, int client_height, DWORD style, DWORD ex_style)
{
    RECT rect{0, 0, client_width, client_height};

    using AdjustWindowRectExForDpiFn = BOOL(WINAPI*)(LPRECT, DWORD, BOOL, DWORD, UINT);
    static const auto adjust_for_dpi = reinterpret_cast<AdjustWindowRectExForDpiFn>(
        GetProcAddress(GetModuleHandleW(L"user32.dll"), "AdjustWindowRectExForDpi"));

    if (adjust_for_dpi)
    {
        adjust_for_dpi(&rect, style, FALSE, ex_style, GetDpiForSystem());
    }
    else
    {
        AdjustWindowRectEx(&rect, style, FALSE, ex_style);
    }

    return rect;
}

void GetCenteredWindowBounds(int client_width, int client_height, DWORD style, DWORD ex_style, int& x, int& y, int& width, int& height)
{
    const RECT outer = AdjustWindowRectForClient(client_width, client_height, style, ex_style);
    width = outer.right - outer.left;
    height = outer.bottom - outer.top;

    const RECT work_area = GetPreferredWorkArea();
    x = work_area.left + ((work_area.right - work_area.left) - width) / 2;
    y = work_area.top + ((work_area.bottom - work_area.top) - height) / 2;

    if (x < work_area.left)
    {
        x = work_area.left;
    }
    if (y < work_area.top)
    {
        y = work_area.top;
    }
}

HMENU ControlId(int id)
{
    return reinterpret_cast<HMENU>(static_cast<INT_PTR>(id));
}

void AddTrayIcon(HWND hwnd)
{
    g_notify_icon = {};
    g_notify_icon.cbSize = sizeof(g_notify_icon);
    g_notify_icon.hWnd = hwnd;
    g_notify_icon.uID = kTrayIconId;
    g_notify_icon.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP;
    g_notify_icon.uCallbackMessage = kTrayCallbackMessage;
    g_notify_icon.hIcon = static_cast<HICON>(LoadImageW(
        g_instance,
        MAKEINTRESOURCEW(kAppIconResourceId),
        IMAGE_ICON,
        GetSystemMetrics(SM_CXSMICON),
        GetSystemMetrics(SM_CYSMICON),
        LR_DEFAULTCOLOR));
    if (!g_notify_icon.hIcon)
    {
        g_notify_icon.hIcon = LoadIconW(nullptr, IDI_APPLICATION);
    }
    wcsncpy_s(g_notify_icon.szTip, kAppName, _TRUNCATE);
    Shell_NotifyIconW(NIM_ADD, &g_notify_icon);
}

void RemoveTrayIcon()
{
    Shell_NotifyIconW(NIM_DELETE, &g_notify_icon);
    if (g_notify_icon.hIcon)
    {
        DestroyIcon(g_notify_icon.hIcon);
        g_notify_icon.hIcon = nullptr;
    }
}

void ShowTrayMenu(HWND hwnd)
{
    EnsureMenuIcons();
    HMENU menu = CreatePopupMenu();
    AppendMenuW(menu, MF_OWNERDRAW, kMenuSettings, reinterpret_cast<LPCWSTR>(Tr().settings));
    AppendMenuW(menu, MF_OWNERDRAW, kMenuAbout, reinterpret_cast<LPCWSTR>(Tr().about));
    AppendMenuW(menu, MF_SEPARATOR, 0, nullptr);
    AppendMenuW(menu, MF_OWNERDRAW, kMenuExit, reinterpret_cast<LPCWSTR>(Tr().exit_app));

    POINT cursor{};
    GetCursorPos(&cursor);
    SetForegroundWindow(hwnd);
    TrackPopupMenu(menu, TPM_BOTTOMALIGN | TPM_LEFTALIGN, cursor.x, cursor.y, 0, hwnd, nullptr);
    DestroyMenu(menu);
}

bool IsAdmin()
{
    return IsUserAnAdmin();
}

bool RelaunchAsAdmin()
{
    wchar_t params[1024] = {};
    if (__argc > 1)
    {
        std::wstring joined;
        for (int i = 1; i < __argc; ++i)
        {
            if (i > 1)
            {
                joined += L' ';
            }
            joined += L"\"";
            joined += __wargv[i];
            joined += L"\"";
        }
        wcsncpy_s(params, joined.c_str(), _TRUNCATE);
    }

    const HINSTANCE result = ShellExecuteW(nullptr, L"runas", GetExecutablePath().c_str(), params[0] ? params : nullptr, nullptr, SW_SHOWNORMAL);
    return reinterpret_cast<INT_PTR>(result) > 32;
}

void CloseKernelHandle(HANDLE& handle)
{
    if (handle)
    {
        CloseHandle(handle);
        handle = nullptr;
    }
}

bool EnsureAutoClickStopEvent()
{
    if (g_auto_click_stop_event)
    {
        return true;
    }

    g_auto_click_stop_event = CreateEventW(nullptr, TRUE, FALSE, nullptr);
    return g_auto_click_stop_event != nullptr;
}

void CleanupFinishedAutoClickThread()
{
    if (g_auto_click_thread && WaitForSingleObject(g_auto_click_thread, 0) == WAIT_OBJECT_0)
    {
        CloseKernelHandle(g_auto_click_thread);
    }
}

void PerformClick()
{
    INPUT inputs[2]{};
    inputs[0].type = INPUT_MOUSE;
    inputs[0].mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
    inputs[0].mi.dwExtraInfo = kInjectedClickMarker;
    inputs[1].type = INPUT_MOUSE;
    inputs[1].mi.dwFlags = MOUSEEVENTF_LEFTUP;
    inputs[1].mi.dwExtraInfo = kInjectedClickMarker;

    SendInput(2, inputs, sizeof(INPUT));
}

DWORD WINAPI AutoClickThreadProc(LPVOID)
{
    HANDLE timer = CreateWaitableTimerW(nullptr, FALSE, nullptr);
    if (!timer)
    {
        g_auto_clicking.store(false);
        return 1;
    }

    const int interval_ms = std::clamp(g_config.auto_click_interval, 10, 500);
    LARGE_INTEGER due_time{};
    due_time.QuadPart = -static_cast<LONGLONG>(interval_ms) * 10000;

    if (!SetWaitableTimer(timer, &due_time, interval_ms, nullptr, nullptr, FALSE))
    {
        CloseHandle(timer);
        g_auto_clicking.store(false);
        return 1;
    }

    HANDLE wait_handles[2]{g_auto_click_stop_event, timer};
    DWORD exit_code = 0;

    while (true)
    {
        const DWORD wait_result = WaitForMultipleObjects(2, wait_handles, FALSE, INFINITE);
        if (wait_result == WAIT_OBJECT_0)
        {
            break;
        }

        if (wait_result == WAIT_OBJECT_0 + 1)
        {
            if (!g_button_held.load())
            {
                break;
            }

            PerformClick();
            continue;
        }

        exit_code = 1;
        break;
    }

    CancelWaitableTimer(timer);
    CloseHandle(timer);
    g_auto_clicking.store(false);
    return exit_code;
}

void StopAutoClick()
{
    g_auto_clicking.store(false);

    if (g_auto_click_stop_event)
    {
        SetEvent(g_auto_click_stop_event);
    }

    if (g_auto_click_thread)
    {
        WaitForSingleObject(g_auto_click_thread, kAutoClickThreadJoinTimeoutMs);
        CloseKernelHandle(g_auto_click_thread);
    }
}

void StartAutoClick()
{
    CleanupFinishedAutoClickThread();
    if (g_auto_clicking.load())
    {
        return;
    }

    if (!EnsureAutoClickStopEvent())
    {
        return;
    }

    ResetEvent(g_auto_click_stop_event);
    g_auto_clicking.store(true);
    g_auto_click_thread = CreateThread(nullptr, 0, AutoClickThreadProc, nullptr, 0, nullptr);
    if (!g_auto_click_thread)
    {
        g_auto_clicking.store(false);
        SetEvent(g_auto_click_stop_event);
    }
}

bool MeetsRapidClickCondition()
{
    if (g_press_times.size() < static_cast<size_t>(g_config.trigger_click_count))
    {
        return false;
    }

    const size_t start_index = g_press_times.size() - static_cast<size_t>(g_config.trigger_click_count);
    const ULONGLONG first = g_press_times[start_index];
    const ULONGLONG last = g_press_times.back();
    return last >= first && (last - first) <= static_cast<ULONGLONG>(g_config.trigger_click_interval);
}

void SetWindowTextSafe(HWND hwnd, const wchar_t* text)
{
    if (hwnd)
    {
        SetWindowTextW(hwnd, text);
    }
}

void RefreshSettingsWindowTexts()
{
    if (!g_settings_window)
    {
        return;
    }

    SetWindowTextW(g_settings_window, Tr().settings_title);
    SetWindowTextSafe(GetDlgItem(g_settings_window, 4101), Tr().mouse_settings);
    SetWindowTextSafe(GetDlgItem(g_settings_window, 4102), Tr().app_settings);
    SetWindowTextSafe(GetDlgItem(g_settings_window, 4201), Tr().trigger_click_count);
    SetWindowTextSafe(GetDlgItem(g_settings_window, 4202), Tr().trigger_click_interval);
    SetWindowTextSafe(GetDlgItem(g_settings_window, 4203), Tr().auto_click_interval);
    SetWindowTextSafe(GetDlgItem(g_settings_window, 4204), Tr().language);
    SetWindowTextSafe(GetDlgItem(g_settings_window, kControlLanguageEn), Tr().english);
    SetWindowTextSafe(GetDlgItem(g_settings_window, kControlLanguageZh), Tr().chinese);
    SetWindowTextSafe(GetDlgItem(g_settings_window, kControlAutoStart), Tr().auto_start);
    SetWindowTextSafe(GetDlgItem(g_settings_window, kControlSave), Tr().save);
    SetWindowTextSafe(GetDlgItem(g_settings_window, kControlCancel), Tr().cancel);
    SetWindowTextSafe(GetDlgItem(g_settings_window, kSettingsInfoText), g_config.language == L"zh"
        ? L"\u6309\u4f4f\u5de6\u952e\u65f6\u81ea\u52a8\u8fde\u70b9\uff0c\u677e\u5f00\u7acb\u5373\u505c\u6b62\u3002"
        : L"Auto-click keeps firing while the left button stays held and stops on release.");
}

void RefreshAboutWindowTexts()
{
    if (!g_about_window)
    {
        return;
    }

    SetWindowTextW(g_about_window, Tr().about_title);
    SetWindowTextSafe(GetDlgItem(g_about_window, 5101), Tr().about_description);
    SetWindowTextSafe(GetDlgItem(g_about_window, 5102), Tr().details);
    SetWindowTextSafe(GetDlgItem(g_about_window, 5103), Tr().version);
    SetWindowTextSafe(GetDlgItem(g_about_window, 5104), Tr().author);
    SetWindowTextSafe(GetDlgItem(g_about_window, 5105), Tr().github);
    SetWindowTextSafe(GetDlgItem(g_about_window, kAboutOk), Tr().ok);
}

LRESULT CALLBACK MouseProc(int code, WPARAM w_param, LPARAM l_param)
{
    if (code >= 0)
    {
        const auto* info = reinterpret_cast<const MSLLHOOKSTRUCT*>(l_param);
        const bool is_program_click =
            (info->flags & LLMHF_INJECTED) != 0 && info->dwExtraInfo == kInjectedClickMarker;
        if (!is_program_click)
        {
            if (w_param == WM_LBUTTONDOWN || w_param == WM_LBUTTONUP)
            {
                const ULONGLONG now = GetTickCount64();
                if (w_param == WM_LBUTTONDOWN)
                {
                    if (g_last_press_tick != 0 && now > g_last_press_tick &&
                        (now - g_last_press_tick) > static_cast<ULONGLONG>(g_config.trigger_click_interval))
                    {
                        g_press_times.clear();
                    }

                    g_button_held.store(true);
                    g_last_press_tick = now;
                    g_press_times.push_back(now);
                    while (g_press_times.size() > 50)
                    {
                        g_press_times.pop_front();
                    }

                    if (MeetsRapidClickCondition())
                    {
                        PostMessageW(g_main_window, kStartAutoClickMessage, 0, 0);
                    }
                }
                else
                {
                    g_button_held.store(false);
                    PostMessageW(g_main_window, kStopAutoClickMessage, 0, 0);
                }
            }
        }
    }

    return CallNextHookEx(g_mouse_hook, code, w_param, l_param);
}

void CreateSettingsControls(HWND hwnd)
{
    const int margin_x = ScaleForDpi(20);
    const int section_y = ScaleForDpi(20);
    const int label_width = ScaleForDpi(180);
    const int input_x = ScaleForDpi(220);
    const int input_width = ScaleForDpi(120);
    const int row_height = ScaleForDpi(24);

    CreateWindowW(L"STATIC", Tr().mouse_settings, WS_CHILD | WS_VISIBLE | SS_LEFT, margin_x, section_y, ScaleForDpi(320), row_height, hwnd, ControlId(4101), g_instance, nullptr);

    CreateWindowW(L"STATIC", Tr().trigger_click_count, WS_CHILD | WS_VISIBLE | SS_LEFT, margin_x, ScaleForDpi(60), label_width, row_height, hwnd, ControlId(4201), g_instance, nullptr);
    HWND trigger_count = CreateWindowExW(WS_EX_CLIENTEDGE, UPDOWN_CLASSW, nullptr, WS_CHILD | WS_VISIBLE | UDS_ALIGNRIGHT | UDS_SETBUDDYINT | UDS_ARROWKEYS, 0, 0, 0, 0, hwnd, nullptr, g_instance, nullptr);
    HWND trigger_edit = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", nullptr, WS_CHILD | WS_VISIBLE | ES_NUMBER | ES_AUTOHSCROLL, input_x, ScaleForDpi(58), input_width, row_height, hwnd, ControlId(kControlTriggerCount), g_instance, nullptr);
    SendMessageW(trigger_count, UDM_SETBUDDY, reinterpret_cast<WPARAM>(trigger_edit), 0);
    SendMessageW(trigger_count, UDM_SETRANGE32, 2, 10);

    CreateWindowW(L"STATIC", Tr().trigger_click_interval, WS_CHILD | WS_VISIBLE | SS_LEFT, margin_x, ScaleForDpi(100), label_width, row_height, hwnd, ControlId(4202), g_instance, nullptr);
    HWND trigger_interval = CreateWindowExW(WS_EX_CLIENTEDGE, UPDOWN_CLASSW, nullptr, WS_CHILD | WS_VISIBLE | UDS_ALIGNRIGHT | UDS_SETBUDDYINT | UDS_ARROWKEYS, 0, 0, 0, 0, hwnd, nullptr, g_instance, nullptr);
    HWND trigger_interval_edit = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", nullptr, WS_CHILD | WS_VISIBLE | ES_NUMBER | ES_AUTOHSCROLL, input_x, ScaleForDpi(98), input_width, row_height, hwnd, ControlId(kControlTriggerInterval), g_instance, nullptr);
    SendMessageW(trigger_interval, UDM_SETBUDDY, reinterpret_cast<WPARAM>(trigger_interval_edit), 0);
    SendMessageW(trigger_interval, UDM_SETRANGE32, 100, 1000);

    CreateWindowW(L"STATIC", Tr().auto_click_interval, WS_CHILD | WS_VISIBLE | SS_LEFT, margin_x, ScaleForDpi(140), label_width, row_height, hwnd, ControlId(4203), g_instance, nullptr);
    HWND auto_interval = CreateWindowExW(WS_EX_CLIENTEDGE, UPDOWN_CLASSW, nullptr, WS_CHILD | WS_VISIBLE | UDS_ALIGNRIGHT | UDS_SETBUDDYINT | UDS_ARROWKEYS, 0, 0, 0, 0, hwnd, nullptr, g_instance, nullptr);
    HWND auto_interval_edit = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", nullptr, WS_CHILD | WS_VISIBLE | ES_NUMBER | ES_AUTOHSCROLL, input_x, ScaleForDpi(138), input_width, row_height, hwnd, ControlId(kControlAutoClickInterval), g_instance, nullptr);
    SendMessageW(auto_interval, UDM_SETBUDDY, reinterpret_cast<WPARAM>(auto_interval_edit), 0);
    SendMessageW(auto_interval, UDM_SETRANGE32, 10, 500);

    CreateWindowW(L"STATIC", Tr().app_settings, WS_CHILD | WS_VISIBLE | SS_LEFT, margin_x, ScaleForDpi(190), ScaleForDpi(320), row_height, hwnd, ControlId(4102), g_instance, nullptr);
    CreateWindowW(L"STATIC", Tr().language, WS_CHILD | WS_VISIBLE | SS_LEFT, margin_x, ScaleForDpi(230), label_width, row_height, hwnd, ControlId(4204), g_instance, nullptr);
    CreateWindowW(L"BUTTON", Tr().english, WS_CHILD | WS_VISIBLE | BS_AUTORADIOBUTTON, input_x, ScaleForDpi(228), ScaleForDpi(80), row_height, hwnd, ControlId(kControlLanguageEn), g_instance, nullptr);
    CreateWindowW(L"BUTTON", Tr().chinese, WS_CHILD | WS_VISIBLE | BS_AUTORADIOBUTTON, ScaleForDpi(310), ScaleForDpi(228), ScaleForDpi(80), row_height, hwnd, ControlId(kControlLanguageZh), g_instance, nullptr);
    CreateWindowW(L"BUTTON", Tr().auto_start, WS_CHILD | WS_VISIBLE | BS_AUTOCHECKBOX, input_x, ScaleForDpi(268), ScaleForDpi(220), row_height, hwnd, ControlId(kControlAutoStart), g_instance, nullptr);
    CreateWindowW(L"STATIC", g_config.language == L"zh"
        ? L"\u6309\u4f4f\u5de6\u952e\u65f6\u81ea\u52a8\u8fde\u70b9\uff0c\u677e\u5f00\u7acb\u5373\u505c\u6b62\u3002"
        : L"Auto-click keeps firing while the left button stays held and stops on release.",
        WS_CHILD | WS_VISIBLE | SS_LEFT,
        margin_x,
        ScaleForDpi(296),
        ScaleForDpi(360),
        ScaleForDpi(18),
        hwnd,
        ControlId(kSettingsInfoText),
        g_instance,
        nullptr);
    CreateWindowW(L"BUTTON", Tr().save, WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON, ScaleForDpi(170), ScaleForDpi(332), ScaleForDpi(100), ScaleForDpi(30), hwnd, ControlId(kControlSave), g_instance, nullptr);
    CreateWindowW(L"BUTTON", Tr().cancel, WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON, ScaleForDpi(290), ScaleForDpi(332), ScaleForDpi(100), ScaleForDpi(30), hwnd, ControlId(kControlCancel), g_instance, nullptr);

    SetDlgItemInt(hwnd, kControlTriggerCount, g_config.trigger_click_count, FALSE);
    SetDlgItemInt(hwnd, kControlTriggerInterval, g_config.trigger_click_interval, FALSE);
    SetDlgItemInt(hwnd, kControlAutoClickInterval, g_config.auto_click_interval, FALSE);
    CheckRadioButton(hwnd, kControlLanguageEn, kControlLanguageZh, g_config.language == L"zh" ? kControlLanguageZh : kControlLanguageEn);
    SendDlgItemMessageW(hwnd, kControlAutoStart, BM_SETCHECK, g_config.auto_start ? BST_CHECKED : BST_UNCHECKED, 0);
    ApplyControlFonts(hwnd);
}

void CreateAboutControls(HWND hwnd)
{
    const int margin_x = ScaleForDpi(20);
    const int value_x = ScaleForDpi(150);
    const int width = ScaleForDpi(420);
    const int row_height = ScaleForDpi(24);

    CreateWindowW(L"STATIC", Tr().about_description, WS_CHILD | WS_VISIBLE | SS_LEFT, margin_x, ScaleForDpi(20), width, ScaleForDpi(40), hwnd, ControlId(5101), g_instance, nullptr);
    CreateWindowW(L"STATIC", Tr().details, WS_CHILD | WS_VISIBLE | SS_LEFT, margin_x, ScaleForDpi(80), ScaleForDpi(120), row_height, hwnd, ControlId(5102), g_instance, nullptr);
    CreateWindowW(L"STATIC", Tr().version, WS_CHILD | WS_VISIBLE | SS_LEFT, margin_x, ScaleForDpi(120), ScaleForDpi(120), row_height, hwnd, ControlId(5103), g_instance, nullptr);
    CreateWindowW(L"STATIC", L"1.1.1", WS_CHILD | WS_VISIBLE | SS_LEFT, value_x, ScaleForDpi(120), ScaleForDpi(240), row_height, hwnd, ControlId(kAboutVersionValue), g_instance, nullptr);
    CreateWindowW(L"STATIC", Tr().author, WS_CHILD | WS_VISIBLE | SS_LEFT, margin_x, ScaleForDpi(150), ScaleForDpi(120), row_height, hwnd, ControlId(5104), g_instance, nullptr);
    CreateWindowW(L"STATIC", L"yanstu", WS_CHILD | WS_VISIBLE | SS_LEFT, value_x, ScaleForDpi(150), ScaleForDpi(240), row_height, hwnd, ControlId(kAboutAuthorValue), g_instance, nullptr);
    CreateWindowW(L"STATIC", Tr().github, WS_CHILD | WS_VISIBLE | SS_LEFT, margin_x, ScaleForDpi(182), ScaleForDpi(120), row_height, hwnd, ControlId(5105), g_instance, nullptr);
    CreateWindowW(L"BUTTON", L"https://github.com/yanstu/RapidClicker", WS_CHILD | WS_VISIBLE | BS_FLAT, value_x, ScaleForDpi(176), ScaleForDpi(250), ScaleForDpi(28), hwnd, ControlId(kGithubLink), g_instance, nullptr);
    CreateWindowW(L"BUTTON", Tr().ok, WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON, ScaleForDpi(180), ScaleForDpi(230), ScaleForDpi(100), ScaleForDpi(30), hwnd, ControlId(kAboutOk), g_instance, nullptr);
    ApplyControlFonts(hwnd);
}

LRESULT CALLBACK SettingsWndProc(HWND hwnd, UINT message, WPARAM w_param, LPARAM l_param)
{
    switch (message)
    {
    case WM_CREATE:
        CreateSettingsControls(hwnd);
        return 0;
    case WM_CTLCOLORSTATIC:
    case WM_CTLCOLORBTN:
    {
        HDC dc = reinterpret_cast<HDC>(w_param);
        SetBkMode(dc, TRANSPARENT);
        SetTextColor(dc, RGB(30, 30, 30));
        return reinterpret_cast<INT_PTR>(g_window_brush);
    }
    case WM_COMMAND:
        switch (LOWORD(w_param))
        {
        case kControlSave:
        {
            BOOL ok_count = FALSE;
            BOOL ok_trigger = FALSE;
            BOOL ok_auto = FALSE;
            const int trigger_count = GetDlgItemInt(hwnd, kControlTriggerCount, &ok_count, FALSE);
            const int trigger_interval = GetDlgItemInt(hwnd, kControlTriggerInterval, &ok_trigger, FALSE);
            const int auto_interval = GetDlgItemInt(hwnd, kControlAutoClickInterval, &ok_auto, FALSE);
            if (!ok_count || !ok_trigger || !ok_auto)
            {
                MessageBoxW(hwnd, Tr().save_failed, kAppName, MB_ICONERROR | MB_OK);
                return 0;
            }

            g_config.trigger_click_count = std::clamp(trigger_count, 2, 10);
            g_config.trigger_click_interval = std::clamp(trigger_interval, 100, 1000);
            g_config.auto_click_interval = std::clamp(auto_interval, 10, 500);
            g_config.language = (IsDlgButtonChecked(hwnd, kControlLanguageZh) == BST_CHECKED) ? L"zh" : L"en";
            g_config.auto_start = IsDlgButtonChecked(hwnd, kControlAutoStart) == BST_CHECKED;

            if (SaveConfig())
            {
                RefreshSettingsWindowTexts();
                RefreshAboutWindowTexts();
                MessageBoxW(hwnd, Tr().settings_saved, kAppName, MB_ICONINFORMATION | MB_OK);
                DestroyWindow(hwnd);
            }
            else
            {
                MessageBoxW(hwnd, Tr().save_failed, kAppName, MB_ICONERROR | MB_OK);
            }
            return 0;
        }
        case kControlCancel:
            DestroyWindow(hwnd);
            return 0;
        default:
            break;
        }
        break;
    case WM_CLOSE:
        DestroyWindow(hwnd);
        return 0;
    case WM_DESTROY:
        g_settings_window = nullptr;
        return 0;
    default:
        break;
    }

    return DefWindowProcW(hwnd, message, w_param, l_param);
}

LRESULT CALLBACK AboutWndProc(HWND hwnd, UINT message, WPARAM w_param, LPARAM l_param)
{
    switch (message)
    {
    case WM_CREATE:
        CreateAboutControls(hwnd);
        return 0;
    case WM_CTLCOLORSTATIC:
    case WM_CTLCOLORBTN:
    {
        HDC dc = reinterpret_cast<HDC>(w_param);
        SetBkMode(dc, TRANSPARENT);
        SetTextColor(dc, RGB(30, 30, 30));
        return reinterpret_cast<INT_PTR>(g_window_brush);
    }
    case WM_COMMAND:
        switch (LOWORD(w_param))
        {
        case kAboutOk:
            DestroyWindow(hwnd);
            return 0;
        case kGithubLink:
            ShellExecuteW(hwnd, L"open", L"https://github.com/yanstu/RapidClicker", nullptr, nullptr, SW_SHOWNORMAL);
            return 0;
        default:
            break;
        }
        break;
    case WM_CLOSE:
        DestroyWindow(hwnd);
        return 0;
    case WM_DESTROY:
        g_about_window = nullptr;
        return 0;
    default:
        break;
    }

    return DefWindowProcW(hwnd, message, w_param, l_param);
}

void ShowSettingsWindow()
{
    if (g_settings_window)
    {
        ShowWindow(g_settings_window, SW_SHOWNORMAL);
        SetForegroundWindow(g_settings_window);
        return;
    }

    const DWORD style = WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU;
    const DWORD ex_style = WS_EX_DLGMODALFRAME;
    int x = 0;
    int y = 0;
    int width = 0;
    int height = 0;
    GetCenteredWindowBounds(ScaleForDpi(430), ScaleForDpi(395), style, ex_style, x, y, width, height);

    g_settings_window = CreateWindowExW(
        ex_style,
        kSettingsClassName,
        Tr().settings_title,
        style,
        x,
        y,
        width,
        height,
        g_main_window,
        nullptr,
        g_instance,
        nullptr);

    ShowWindow(g_settings_window, SW_SHOWNORMAL);
    UpdateWindow(g_settings_window);
}

void ShowAboutWindow()
{
    if (g_about_window)
    {
        ShowWindow(g_about_window, SW_SHOWNORMAL);
        SetForegroundWindow(g_about_window);
        return;
    }

    const DWORD style = WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU;
    const DWORD ex_style = WS_EX_DLGMODALFRAME;
    int x = 0;
    int y = 0;
    int width = 0;
    int height = 0;
    GetCenteredWindowBounds(ScaleForDpi(450), ScaleForDpi(300), style, ex_style, x, y, width, height);

    g_about_window = CreateWindowExW(
        ex_style,
        kAboutClassName,
        Tr().about_title,
        style,
        x,
        y,
        width,
        height,
        g_main_window,
        nullptr,
        g_instance,
        nullptr);

    ShowWindow(g_about_window, SW_SHOWNORMAL);
    UpdateWindow(g_about_window);
}

LRESULT CALLBACK MainWndProc(HWND hwnd, UINT message, WPARAM w_param, LPARAM l_param)
{
    switch (message)
    {
    case WM_CREATE:
        AddTrayIcon(hwnd);
        return 0;
    case kTrayCallbackMessage:
        if (l_param == WM_RBUTTONUP || l_param == WM_CONTEXTMENU)
        {
            ShowTrayMenu(hwnd);
        }
        else if (l_param == WM_LBUTTONDBLCLK)
        {
            ShowSettingsWindow();
        }
        return 0;
    case WM_COMMAND:
        switch (LOWORD(w_param))
        {
        case kMenuSettings:
            ShowSettingsWindow();
            return 0;
        case kMenuAbout:
            ShowAboutWindow();
            return 0;
        case kMenuExit:
            DestroyWindow(hwnd);
            return 0;
        default:
            break;
        }
        break;
    case WM_MEASUREITEM:
    {
        auto* measure = reinterpret_cast<MEASUREITEMSTRUCT*>(l_param);
        if (measure && measure->CtlType == ODT_MENU)
        {
            const wchar_t* text = reinterpret_cast<const wchar_t*>(measure->itemData);
            HDC dc = GetDC(hwnd);
            HGDIOBJ old_font = SelectObject(dc, g_ui_font);
            SIZE text_size{};
            GetTextExtentPoint32W(dc, text ? text : L"", text ? static_cast<int>(wcslen(text)) : 0, &text_size);
            SelectObject(dc, old_font);
            ReleaseDC(hwnd, dc);

            measure->itemHeight = std::max(ScaleForDpi(26), static_cast<int>(text_size.cy) + ScaleForDpi(10));
            measure->itemWidth = ScaleForDpi(18 + 10 + 8 + 12) + text_size.cx;
            return TRUE;
        }
        break;
    }
    case WM_DRAWITEM:
    {
        auto* draw = reinterpret_cast<DRAWITEMSTRUCT*>(l_param);
        if (draw && draw->CtlType == ODT_MENU)
        {
            const bool selected = (draw->itemState & ODS_SELECTED) != 0;
            const RECT& rc = draw->rcItem;
            FillRect(draw->hDC, &rc, GetSysColorBrush(selected ? COLOR_HIGHLIGHT : COLOR_MENU));

            const int icon_size = ScaleForDpi(16);
            const int icon_left = rc.left + ScaleForDpi(10);
            const int icon_top = rc.top + ((rc.bottom - rc.top) - icon_size) / 2;
            if (HICON icon = GetMenuIcon(draw->itemID))
            {
                DrawIconEx(draw->hDC, icon_left, icon_top, icon, icon_size, icon_size, 0, nullptr, DI_NORMAL);
            }

            RECT text_rect{
                icon_left + icon_size + ScaleForDpi(8),
                rc.top,
                rc.right - ScaleForDpi(12),
                rc.bottom};
            SetBkMode(draw->hDC, TRANSPARENT);
            SetTextColor(draw->hDC, GetSysColor(selected ? COLOR_HIGHLIGHTTEXT : COLOR_MENUTEXT));
            HGDIOBJ old_font = SelectObject(draw->hDC, g_ui_font);
            const wchar_t* text = reinterpret_cast<const wchar_t*>(draw->itemData);
            DrawTextW(draw->hDC, text ? text : L"", -1, &text_rect, DT_LEFT | DT_SINGLELINE | DT_VCENTER | DT_NOPREFIX);
            SelectObject(draw->hDC, old_font);
            return TRUE;
        }
        break;
    }
    case kStartAutoClickMessage:
        if (g_button_held.load())
        {
            StartAutoClick();
        }
        return 0;
    case kStopAutoClickMessage:
        StopAutoClick();
        return 0;
    case WM_CLOSE:
        DestroyWindow(hwnd);
        return 0;
    case WM_DESTROY:
        StopAutoClick();
        CloseKernelHandle(g_auto_click_stop_event);
        RemoveTrayIcon();
        if (g_mouse_hook)
        {
            UnhookWindowsHookEx(g_mouse_hook);
            g_mouse_hook = nullptr;
        }
        if (g_menu_icon_settings)
        {
            DestroyIcon(g_menu_icon_settings);
            g_menu_icon_settings = nullptr;
        }
        if (g_menu_icon_about)
        {
            DestroyIcon(g_menu_icon_about);
            g_menu_icon_about = nullptr;
        }
        if (g_menu_icon_exit)
        {
            DestroyIcon(g_menu_icon_exit);
            g_menu_icon_exit = nullptr;
        }
        if (g_ui_font)
        {
            DeleteObject(g_ui_font);
            g_ui_font = nullptr;
        }
        if (g_ui_font_bold)
        {
            DeleteObject(g_ui_font_bold);
            g_ui_font_bold = nullptr;
        }
        if (g_window_brush)
        {
            DeleteObject(g_window_brush);
            g_window_brush = nullptr;
        }
        PostQuitMessage(0);
        return 0;
    default:
        break;
    }

    return DefWindowProcW(hwnd, message, w_param, l_param);
}

bool RegisterWindowClasses()
{
    HICON app_icon = static_cast<HICON>(LoadImageW(
        g_instance,
        MAKEINTRESOURCEW(kAppIconResourceId),
        IMAGE_ICON,
        GetSystemMetrics(SM_CXICON),
        GetSystemMetrics(SM_CYICON),
        LR_DEFAULTCOLOR));

    WNDCLASSW main_class{};
    main_class.lpfnWndProc = MainWndProc;
    main_class.hInstance = g_instance;
    main_class.lpszClassName = kWindowClassName;
    main_class.hCursor = LoadCursorW(nullptr, IDC_ARROW);
    main_class.hIcon = app_icon ? app_icon : LoadIconW(nullptr, IDI_APPLICATION);
    if (!RegisterClassW(&main_class))
    {
        return false;
    }

    WNDCLASSW settings_class{};
    settings_class.lpfnWndProc = SettingsWndProc;
    settings_class.hInstance = g_instance;
    settings_class.lpszClassName = kSettingsClassName;
    settings_class.hCursor = LoadCursorW(nullptr, IDC_ARROW);
    settings_class.hbrBackground = reinterpret_cast<HBRUSH>(COLOR_WINDOW + 1);
    settings_class.hIcon = app_icon ? app_icon : LoadIconW(nullptr, IDI_APPLICATION);
    if (!RegisterClassW(&settings_class))
    {
        return false;
    }

    WNDCLASSW about_class{};
    about_class.lpfnWndProc = AboutWndProc;
    about_class.hInstance = g_instance;
    about_class.lpszClassName = kAboutClassName;
    about_class.hCursor = LoadCursorW(nullptr, IDC_ARROW);
    about_class.hbrBackground = reinterpret_cast<HBRUSH>(COLOR_WINDOW + 1);
    about_class.hIcon = app_icon ? app_icon : LoadIconW(nullptr, IDI_APPLICATION);
    return RegisterClassW(&about_class) != 0;
}

} // namespace

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE, PWSTR, int)
{
    g_instance = instance;
    SetProcessDPIAware();
    InitCommonControls();
    EnsureUiResources();
    LoadConfig();

    if (!IsAdmin())
    {
        if (RelaunchAsAdmin())
        {
            return 0;
        }
    }

    g_mutex = CreateMutexW(nullptr, FALSE, kMutexName);
    if (!g_mutex || GetLastError() == ERROR_ALREADY_EXISTS)
    {
        MessageBoxW(nullptr, Tr().already_running, kAppName, MB_ICONINFORMATION | MB_OK);
        if (g_mutex)
        {
            CloseHandle(g_mutex);
        }
        return 0;
    }

    if (!RegisterWindowClasses())
    {
        MessageBoxW(nullptr, L"Failed to register window classes.", kAppName, MB_ICONERROR | MB_OK);
        CloseHandle(g_mutex);
        return 1;
    }

    g_main_window = CreateWindowExW(
        0,
        kWindowClassName,
        kAppName,
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        300,
        200,
        nullptr,
        nullptr,
        instance,
        nullptr);

    if (!g_main_window)
    {
        MessageBoxW(nullptr, L"Failed to create main window.", kAppName, MB_ICONERROR | MB_OK);
        CloseHandle(g_mutex);
        return 1;
    }

    HICON app_icon_small = static_cast<HICON>(LoadImageW(
        g_instance,
        MAKEINTRESOURCEW(kAppIconResourceId),
        IMAGE_ICON,
        GetSystemMetrics(SM_CXSMICON),
        GetSystemMetrics(SM_CYSMICON),
        LR_DEFAULTCOLOR));
    if (app_icon_small)
    {
        SendMessageW(g_main_window, WM_SETICON, ICON_SMALL, reinterpret_cast<LPARAM>(app_icon_small));
    }

    ShowWindow(g_main_window, SW_HIDE);
    UpdateWindow(g_main_window);

    g_mouse_hook = SetWindowsHookExW(WH_MOUSE_LL, MouseProc, nullptr, 0);
    if (!g_mouse_hook)
    {
        MessageBoxW(nullptr, L"Failed to install mouse hook.", kAppName, MB_ICONERROR | MB_OK);
        DestroyWindow(g_main_window);
        CloseHandle(g_mutex);
        return 1;
    }

    MSG msg{};
    while (GetMessageW(&msg, nullptr, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }

    if (g_mutex)
    {
        CloseHandle(g_mutex);
        g_mutex = nullptr;
    }

    return 0;
}
