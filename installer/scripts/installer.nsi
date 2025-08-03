; Professional NSIS Installer for Chicken Farm Manager
; Modern UI with complete Windows integration

!include "MUI2.nsh"
!include "WinVer.nsh"
!include "x64.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

; Application Information
!define APP_NAME "Phần mềm Quản lý Cám - Trại Gà"
!define APP_NAME_SHORT "ChickenFarmManager"
!define APP_VERSION "2.0.0"
!define APP_PUBLISHER "Minh-Tan_Phat"
!define APP_URL "https://github.com/Minh-Tan_Phat"
!define APP_DESCRIPTION "Professional Chicken Farm Management System"
!define APP_COPYRIGHT "© 2025 Minh-Tan_Phat. All rights reserved."

; Installer Information
!define INSTALLER_NAME "${APP_NAME_SHORT}_Setup.exe"
!define UNINSTALLER_NAME "Uninstall.exe"

; Registry Keys
!define REG_UNINSTALL "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME_SHORT}"
!define REG_APP_PATH "Software\${APP_PUBLISHER}\${APP_NAME_SHORT}"

; Paths
!define SOURCE_DIR "..\output"
!define RESOURCES_DIR "..\resources"

; Installer Settings
Name "${APP_NAME}"
OutFile "${INSTALLER_NAME}"
InstallDir "$PROGRAMFILES64\${APP_NAME_SHORT}"
InstallDirRegKey HKLM "${REG_APP_PATH}" "InstallLocation"
RequestExecutionLevel admin
ShowInstDetails show
ShowUnInstDetails show

; Version Information
VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey "LegalCopyright" "${APP_COPYRIGHT}"
VIAddVersionKey "FileDescription" "${APP_DESCRIPTION}"
VIAddVersionKey "FileVersion" "${APP_VERSION}"

; Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "${RESOURCES_DIR}\app_icon.ico"
!define MUI_UNICON "${RESOURCES_DIR}\app_icon.ico"

; Welcome page
!define MUI_WELCOMEPAGE_TITLE "Chào mừng đến với ${APP_NAME}"
!define MUI_WELCOMEPAGE_TEXT "Trình cài đặt sẽ hướng dẫn bạn cài đặt ${APP_NAME}.$\r$\n$\r$\nPhần mềm quản lý chuyên nghiệp cho trại gà với đầy đủ tính năng theo dõi cám, quản lý tồn kho và báo cáo.$\r$\n$\r$\nNhấn Tiếp tục để bắt đầu."

; License page
!define MUI_LICENSEPAGE_TEXT_TOP "Vui lòng đọc thỏa thuận giấy phép trước khi cài đặt ${APP_NAME}."
!define MUI_LICENSEPAGE_TEXT_BOTTOM "Nếu bạn chấp nhận các điều khoản, nhấn Tôi đồng ý để tiếp tục."

; Directory page
!define MUI_DIRECTORYPAGE_TEXT_TOP "Chọn thư mục để cài đặt ${APP_NAME}.$\r$\n$\r$\nTrình cài đặt sẽ cài đặt ${APP_NAME} vào thư mục sau. Để cài đặt vào thư mục khác, nhấn Duyệt và chọn thư mục khác."

; Start Menu page
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "${APP_NAME_SHORT}"
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKLM"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${REG_APP_PATH}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"

; Finish page
!define MUI_FINISHPAGE_TITLE "Hoàn tất cài đặt ${APP_NAME}"
!define MUI_FINISHPAGE_TEXT "${APP_NAME} đã được cài đặt thành công trên máy tính của bạn.$\r$\n$\r$\nNhấn Hoàn tất để đóng trình cài đặt."
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_NAME_SHORT}.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Chạy ${APP_NAME}"
!define MUI_FINISHPAGE_LINK "Truy cập trang web của chúng tôi"
!define MUI_FINISHPAGE_LINK_LOCATION "${APP_URL}"

; Variables
Var StartMenuFolder

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${RESOURCES_DIR}\license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Functions
Function .onInit
    ; Check Windows version
    ${IfNot} ${AtLeastWin10}
        MessageBox MB_OK|MB_ICONSTOP "Phần mềm này yêu cầu Windows 10 hoặc mới hơn."
        Abort
    ${EndIf}

    ; Check if already installed
    ReadRegStr $R0 HKLM "${REG_UNINSTALL}" "UninstallString"
    StrCmp $R0 "" done

    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
        "${APP_NAME} đã được cài đặt. $\n$\nNhấn OK để gỡ cài đặt phiên bản cũ hoặc Cancel để hủy." \
        IDOK uninst
    Abort

    uninst:
        ClearErrors
        ExecWait '$R0 /S _?=$INSTDIR'

        IfErrors no_remove_uninstaller done
        IfFileExists "$INSTDIR\${UNINSTALLER_NAME}" 0 no_remove_uninstaller
        Delete "$INSTDIR\${UNINSTALLER_NAME}"
        RMDir "$INSTDIR"

    no_remove_uninstaller:
    done:
FunctionEnd

; Installation Section
Section "Core Application" SecCore
    SectionIn RO

    ; Set output path
    SetOutPath "$INSTDIR"

    ; Install main executable
    File "${SOURCE_DIR}\${APP_NAME_SHORT}.exe"

    ; Install any additional files (DLLs, etc.)
    File /nonfatal "${SOURCE_DIR}\*.dll"

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\${UNINSTALLER_NAME}"

    ; Write registry information
    WriteRegStr HKLM "${REG_APP_PATH}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "${REG_APP_PATH}" "Version" "${APP_VERSION}"

    ; Write uninstall information
    WriteRegStr HKLM "${REG_UNINSTALL}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "${REG_UNINSTALL}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "${REG_UNINSTALL}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "${REG_UNINSTALL}" "URLInfoAbout" "${APP_URL}"
    WriteRegStr HKLM "${REG_UNINSTALL}" "DisplayIcon" "$INSTDIR\${APP_NAME_SHORT}.exe"
    WriteRegStr HKLM "${REG_UNINSTALL}" "UninstallString" "$INSTDIR\${UNINSTALLER_NAME}"
    WriteRegStr HKLM "${REG_UNINSTALL}" "QuietUninstallString" "$INSTDIR\${UNINSTALLER_NAME} /S"
    WriteRegDWORD HKLM "${REG_UNINSTALL}" "NoModify" 1
    WriteRegDWORD HKLM "${REG_UNINSTALL}" "NoRepair" 1

    ; Calculate and write size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "${REG_UNINSTALL}" "EstimatedSize" "$0"

SectionEnd

; Start Menu Shortcuts Section
Section "Start Menu Shortcuts" SecStartMenu
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application

    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\${APP_NAME}.lnk" "$INSTDIR\${APP_NAME_SHORT}.exe"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Gỡ cài đặt ${APP_NAME}.lnk" "$INSTDIR\${UNINSTALLER_NAME}"

    !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

; Desktop Shortcut Section
Section "Desktop Shortcut" SecDesktop
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_NAME_SHORT}.exe"
SectionEnd

; Section Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Các tệp chương trình chính. Bắt buộc."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} "Tạo lối tắt trong Start Menu."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Tạo lối tắt trên Desktop."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller Section
Section "Uninstall"
    ; Stop the application if running
    DetailPrint "Đang kiểm tra ứng dụng đang chạy..."
    FindWindow $R0 "" "${APP_NAME}"
    ${If} $R0 != 0
        MessageBox MB_OKCANCEL|MB_ICONQUESTION \
            "${APP_NAME} đang chạy. Vui lòng đóng ứng dụng trước khi gỡ cài đặt." \
            IDOK continue_uninstall
        Abort

        continue_uninstall:
        ; Try to close gracefully first
        SendMessage $R0 ${WM_CLOSE} 0 0
        Sleep 3000

        ; Force close if still running
        ExecWait 'taskkill /F /IM "${APP_NAME_SHORT}.exe"' $R1
    ${EndIf}

    ; Remove files
    DetailPrint "Đang xóa tệp chương trình..."
    Delete "$INSTDIR\${APP_NAME_SHORT}.exe"
    Delete "$INSTDIR\*.dll"
    Delete "$INSTDIR\${UNINSTALLER_NAME}"

    ; Remove user data (ask user first)
    MessageBox MB_YESNO|MB_ICONQUESTION \
        "Bạn có muốn xóa dữ liệu người dùng không?$\n$\n(Bao gồm cài đặt, báo cáo và dữ liệu đã lưu)" \
        IDNO skip_userdata

    ; Remove user data
    DetailPrint "Đang xóa dữ liệu người dùng..."
    RMDir /r "$APPDATA\${APP_NAME_SHORT}"
    RMDir /r "$LOCALAPPDATA\${APP_NAME_SHORT}"

    skip_userdata:

    ; Remove shortcuts
    DetailPrint "Đang xóa lối tắt..."
    !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
    Delete "$SMPROGRAMS\$StartMenuFolder\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\Gỡ cài đặt ${APP_NAME}.lnk"
    RMDir "$SMPROGRAMS\$StartMenuFolder"
    Delete "$DESKTOP\${APP_NAME}.lnk"

    ; Remove registry keys
    DetailPrint "Đang xóa thông tin đăng ký..."
    DeleteRegKey HKLM "${REG_UNINSTALL}"
    DeleteRegKey HKLM "${REG_APP_PATH}"

    ; Remove installation directory
    DetailPrint "Đang xóa thư mục cài đặt..."
    RMDir "$INSTDIR"

    ; Check if directory was removed
    IfFileExists "$INSTDIR" 0 +3
        MessageBox MB_OK|MB_ICONINFORMATION \
            "Một số tệp không thể xóa. Vui lòng xóa thủ công thư mục:$\n$INSTDIR"

SectionEnd

; Uninstaller Functions
Function un.onInit
    MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 \
        "Bạn có chắc chắn muốn gỡ cài đặt ${APP_NAME} và tất cả các thành phần của nó?" \
        IDYES +2
    Abort
FunctionEnd
