; Vietnamese language file for Inno Setup
; Translated by Minh-Tan_Phat

[LangOptions]
LanguageName=Ti<1EBF>ng Vi<1EC7>t
LanguageID=$042A
LanguageCodePage=1258

[Messages]
; *** Application titles
SetupAppTitle=Cài đặt
SetupWindowTitle=Cài đặt - %1
UninstallAppTitle=Gỡ cài đặt
UninstallAppFullTitle=Gỡ cài đặt %1

; *** Misc. common
InformationTitle=Thông tin
ConfirmTitle=Xác nhận
ErrorTitle=Lỗi

; *** SetupLdr messages
SetupLdrStartupMessage=Chương trình sẽ cài đặt %1. Bạn có muốn tiếp tục?
LdrCannotCreateTemp=Không thể tạo file tạm thời. Cài đặt bị hủy
LdrCannotExecTemp=Không thể thực thi file trong thư mục tạm thời. Cài đặt bị hủy

; *** Startup error messages
LastErrorMessage=%1.%n%nLỗi %2: %3
SetupFileMissing=File %1 bị thiếu trong thư mục cài đặt. Vui lòng khắc phục sự cố hoặc lấy bản sao mới của chương trình.
SetupFileCorrupt=File cài đặt bị hỏng. Vui lòng lấy bản sao mới của chương trình.
SetupFileCorruptOrWrongVer=File cài đặt bị hỏng hoặc không tương thích với phiên bản Setup này. Vui lòng khắc phục sự cố hoặc lấy bản sao mới của chương trình.
InvalidParameter=Tham số không hợp lệ được truyền trên dòng lệnh:%n%n%1
SetupAlreadyRunning=Setup đang chạy.
WindowsVersionNotSupported=Chương trình này không hỗ trợ phiên bản Windows mà máy tính của bạn đang chạy.
WindowsServicePackRequired=Chương trình này yêu cầu %1 Service Pack %2 hoặc mới hơn.
NotOnThisPlatform=Chương trình này sẽ không chạy trên %1.
OnlyOnThisPlatform=Chương trình này phải được chạy trên %1.
OnlyOnTheseArchitectures=Chương trình này chỉ có thể được cài đặt trên các phiên bản Windows được thiết kế cho các kiến trúc bộ xử lý sau:%n%n%1
WinVersionTooLowError=Chương trình này yêu cầu %1 phiên bản %2 hoặc mới hơn.
WinVersionTooHighError=Chương trình này không thể được cài đặt trên %1 phiên bản %2 hoặc mới hơn.
AdminPrivilegesRequired=Bạn phải đăng nhập với tư cách quản trị viên khi cài đặt chương trình này.
PowerUserPrivilegesRequired=Bạn phải đăng nhập với tư cách quản trị viên hoặc thành viên của nhóm Power Users khi cài đặt chương trình này.
SetupAppRunningError=Setup đã phát hiện rằng %1 hiện đang chạy.%n%nVui lòng đóng tất cả các phiên bản của nó ngay bây giờ, sau đó nhấp OK để tiếp tục hoặc Hủy để thoát.
UninstallAppRunningError=Gỡ cài đặt đã phát hiện rằng %1 hiện đang chạy.%n%nVui lòng đóng tất cả các phiên bản của nó ngay bây giờ, sau đó nhấp OK để tiếp tục hoặc Hủy để thoát.

; *** Startup questions
PrivilegesRequiredOverrideTitle=Chọn chế độ cài đặt Setup
PrivilegesRequiredOverrideInstruction=Chọn chế độ cài đặt
PrivilegesRequiredOverrideText1=%1 có thể được cài đặt cho tất cả người dùng (yêu cầu đặc quyền quản trị viên) hoặc chỉ cho bạn.
PrivilegesRequiredOverrideText2=%1 có thể được cài đặt chỉ cho bạn hoặc cho tất cả người dùng (yêu cầu đặc quyền quản trị viên).
PrivilegesRequiredOverrideAllUsers=Cài đặt cho &tất cả người dùng
PrivilegesRequiredOverrideAllUsersRecommended=Cài đặt cho &tất cả người dùng (khuyến nghị)
PrivilegesRequiredOverrideCurrentUser=Cài đặt chỉ cho &tôi
PrivilegesRequiredOverrideCurrentUserRecommended=Cài đặt chỉ cho &tôi (khuyến nghị)

; *** Misc. common
ReadyLabel=Sẵn sàng cài đặt
FinishedLabel=Hoàn thành
ClickNext=Nhấp Tiếp theo để tiếp tục hoặc Hủy để thoát khỏi Setup.
ClickInstall=Nhấp Cài đặt để tiếp tục cài đặt.
ClickFinish=Nhấp Hoàn thành để thoát khỏi Setup.
ClickCancel=Nhấp Hủy để thoát khỏi Setup.
ClickYes=Nhấp Có
ClickNo=Nhấp Không
BeveledLabel=
BrowseDialogTitle=Duyệt thư mục
BrowseDialogLabel=Chọn một thư mục trong danh sách bên dưới, sau đó nhấp OK.
NewFolderName=Thư mục mới

; *** "Welcome" wizard page
WelcomeLabel1=Chào mừng đến với Trình hướng dẫn cài đặt [name]
WelcomeLabel2=Điều này sẽ cài đặt [name/ver] trên máy tính của bạn.%n%nBạn nên đóng tất cả các ứng dụng khác trước khi tiếp tục.

; *** "Password" wizard page
WizardPassword=Mật khẩu
PasswordLabel1=Cài đặt này được bảo vệ bằng mật khẩu.
PasswordLabel3=Vui lòng cung cấp mật khẩu, sau đó nhấp Tiếp theo để tiếp tục. Mật khẩu phân biệt chữ hoa chữ thường.
PasswordEditLabel=&Mật khẩu:
IncorrectPassword=Mật khẩu bạn đã nhập không chính xác. Vui lòng thử lại.

; *** "License Agreement" wizard page
WizardLicense=Thỏa thuận giấy phép
LicenseLabel=Vui lòng đọc thông tin quan trọng sau trước khi tiếp tục.
LicenseLabel3=Vui lòng đọc Thỏa thuận giấy phép sau. Bạn phải chấp nhận các điều khoản của thỏa thuận này trước khi tiếp tục cài đặt.
LicenseAccepted=Tôi &chấp nhận thỏa thuận
LicenseNotAccepted=Tôi &không chấp nhận thỏa thuận

; *** "Information" wizard pages
WizardInfoBefore=Thông tin
InfoBeforeLabel=Vui lòng đọc thông tin quan trọng sau trước khi tiếp tục.
InfoBeforeClickLabel=Khi bạn đã sẵn sàng tiếp tục cài đặt, hãy nhấp Tiếp theo.
WizardInfoAfter=Thông tin
InfoAfterLabel=Vui lòng đọc thông tin quan trọng sau trước khi tiếp tục.
InfoAfterClickLabel=Khi bạn đã sẵn sàng tiếp tục cài đặt, hãy nhấp Tiếp theo.

; *** "User Information" wizard page
WizardUserInfo=Thông tin người dùng
UserInfoDesc=Vui lòng nhập thông tin của bạn.
UserInfoName=&Tên người dùng:
UserInfoOrg=&Tổ chức:
UserInfoSerial=&Số sê-ri:
UserInfoNameRequired=Bạn phải nhập tên.

; *** "Select Destination Location" wizard page
WizardSelectDir=Chọn vị trí đích
SelectDirDesc=Nên cài đặt [name] ở đâu?
SelectDirLabel3=Setup sẽ cài đặt [name] vào thư mục sau.
SelectDirBrowseLabel=Để tiếp tục, hãy nhấp Tiếp theo. Nếu bạn muốn chọn một thư mục khác, hãy nhấp Duyệt.
DiskSpaceMBLabel=Ít nhất [mb] MB dung lượng đĩa trống là bắt buộc.
CannotInstallToNetworkDrive=Setup không thể cài đặt vào ổ đĩa mạng.
CannotInstallToUNCPath=Setup không thể cài đặt vào đường dẫn UNC.
InvalidPath=Bạn phải nhập đường dẫn đầy đủ với chữ cái ổ đĩa; ví dụ:%n%nC:\APP%n%nhoặc đường dẫn UNC của biểu mẫu:%n%n\\server\share
InvalidDrive=Ổ đĩa hoặc chia sẻ UNC bạn đã chọn không tồn tại hoặc không thể truy cập. Vui lòng chọn một cái khác.
DiskSpaceWarningTitle=Không đủ dung lượng đĩa
DiskSpaceWarning=Setup yêu cầu ít nhất %1 KB dung lượng trống để cài đặt, nhưng ổ đĩa đã chọn chỉ có %2 KB có sẵn.%n%nBạn có muốn tiếp tục dù sao không?
DirNameTooLong=Tên thư mục hoặc đường dẫn quá dài.
InvalidDirName=Tên thư mục không hợp lệ.
BadDirName32=Tên thư mục không được chứa bất kỳ ký tự nào sau đây:%n%n%1
DirExistsTitle=Thư mục tồn tại
DirExists=Thư mục:%n%n%1%n%nđã tồn tại. Bạn có muốn cài đặt vào thư mục đó dù sao không?
DirDoesntExistTitle=Thư mục không tồn tại
DirDoesntExist=Thư mục:%n%n%1%n%nkhông tồn tại. Bạn có muốn tạo thư mục không?

; *** "Select Components" wizard page
WizardSelectComponents=Chọn thành phần
SelectComponentsDesc=Nên cài đặt những thành phần nào?
SelectComponentsLabel2=Chọn các thành phần bạn muốn cài đặt; xóa các thành phần bạn không muốn cài đặt. Nhấp Tiếp theo khi bạn đã sẵn sàng tiếp tục.
FullInstallation=Cài đặt đầy đủ
CompactInstallation=Cài đặt nhỏ gọn
CustomInstallation=Cài đặt tùy chỉnh
NoUninstallWarningTitle=Thành phần tồn tại
NoUninstallWarning=Setup đã phát hiện rằng các thành phần sau đã được cài đặt trên máy tính của bạn:%n%n%1%n%nBỏ chọn các thành phần này sẽ không gỡ cài đặt chúng.%n%nBạn có muốn tiếp tục dù sao không?
ComponentSize1=%1 KB
ComponentSize2=%1 MB
ComponentsDiskSpaceMBLabel=Lựa chọn hiện tại yêu cầu ít nhất [mb] MB dung lượng đĩa.

; *** "Select Additional Tasks" wizard page
WizardSelectTasks=Chọn tác vụ bổ sung
SelectTasksDesc=Nên thực hiện những tác vụ bổ sung nào?
SelectTasksLabel2=Chọn các tác vụ bổ sung bạn muốn Setup thực hiện trong khi cài đặt [name], sau đó nhấp Tiếp theo.

; *** "Select Start Menu Folder" wizard page
WizardSelectProgramGroup=Chọn thư mục Start Menu
SelectStartMenuFolderDesc=Nên đặt lối tắt của chương trình ở đâu?
SelectStartMenuFolderLabel3=Setup sẽ tạo lối tắt của chương trình trong thư mục Start Menu sau.
SelectStartMenuFolderBrowseLabel=Để tiếp tục, hãy nhấp Tiếp theo. Nếu bạn muốn chọn một thư mục khác, hãy nhấp Duyệt.
MustEnterGroupName=Bạn phải nhập tên nhóm.
GroupNameTooLong=Tên thư mục hoặc đường dẫn quá dài.
InvalidGroupName=Tên thư mục không hợp lệ.
BadGroupName=Tên nhóm không được chứa bất kỳ ký tự nào sau đây:%n%n%1
NoProgramGroupCheck2=&Không tạo thư mục Start Menu

; *** "Ready to Install" wizard page
WizardReady=Sẵn sàng cài đặt
ReadyLabel1=Setup hiện đã sẵn sàng bắt đầu cài đặt [name] trên máy tính của bạn.
ReadyLabel2a=Nhấp Cài đặt để tiếp tục cài đặt hoặc nhấp Quay lại nếu bạn muốn xem lại hoặc thay đổi bất kỳ cài đặt nào.
ReadyLabel2b=Nhấp Cài đặt để tiếp tục cài đặt.
ReadyMemoUserInfo=Thông tin người dùng:
ReadyMemoDir=Vị trí đích:
ReadyMemoType=Loại cài đặt:
ReadyMemoComponents=Thành phần đã chọn:
ReadyMemoGroup=Thư mục Start Menu:
ReadyMemoTasks=Tác vụ bổ sung:

; *** "Preparing to Install" wizard page
WizardPreparing=Chuẩn bị cài đặt
PreparingDesc=Setup đang chuẩn bị cài đặt [name] trên máy tính của bạn.
PreviousInstallNotCompleted=Cài đặt/gỡ cài đặt chương trình trước đó chưa hoàn thành. Bạn sẽ cần khởi động lại máy tính để hoàn thành cài đặt đó.%n%nSau khi khởi động lại máy tính, hãy chạy lại Setup để hoàn thành cài đặt [name].
CannotContinue=Setup không thể tiếp tục. Vui lòng nhấp Hủy để thoát.
ApplicationsFound=Các ứng dụng sau đang sử dụng các tệp cần được cập nhật bởi Setup. Bạn nên cho phép Setup tự động đóng các ứng dụng này.
ApplicationsFound2=Các ứng dụng sau đang sử dụng các tệp cần được cập nhật bởi Setup. Bạn nên cho phép Setup tự động đóng các ứng dụng này. Sau khi cài đặt hoàn tất, Setup sẽ cố gắng khởi động lại các ứng dụng.
CloseApplications=&Tự động đóng các ứng dụng
DontCloseApplications=&Không đóng các ứng dụng
ErrorCloseApplications=Setup không thể tự động đóng tất cả các ứng dụng. Bạn nên đóng tất cả các ứng dụng đang sử dụng các tệp cần được cập nhật bởi Setup trước khi tiếp tục.

; *** "Installing" wizard page
WizardInstalling=Đang cài đặt
InstallingLabel=Vui lòng đợi trong khi Setup cài đặt [name] trên máy tính của bạn.

; *** "Setup Completed" wizard page
FinishedHeadingLabel=Hoàn thành Trình hướng dẫn cài đặt [name]
FinishedLabelNoIcons=Setup đã hoàn thành cài đặt [name] trên máy tính của bạn.
FinishedLabel=Setup đã hoàn thành cài đặt [name] trên máy tính của bạn. Ứng dụng có thể được khởi chạy bằng cách chọn các biểu tượng đã cài đặt.
ClickFinish=Nhấp Hoàn thành để thoát khỏi Setup.
FinishedRestartLabel=Để hoàn thành cài đặt [name], Setup phải khởi động lại máy tính của bạn. Bạn có muốn khởi động lại ngay bây giờ không?
FinishedRestartMessage=Để hoàn thành cài đặt [name], Setup phải khởi động lại máy tính của bạn.%n%nBạn có muốn khởi động lại ngay bây giờ không?
ShowReadmeCheck=Có, tôi muốn xem tệp README
YesRadio=&Có, khởi động lại máy tính ngay bây giờ
NoRadio=&Không, tôi sẽ khởi động lại máy tính sau
RunEntryExec=Chạy %1
RunEntryShellExec=Xem %1

; *** "Setup Needs the Next Disk" stuff
ChangeDiskTitle=Setup cần đĩa tiếp theo
SelectDiskLabel2=Vui lòng chèn Đĩa %1 và nhấp OK.%n%nNếu các tệp trên đĩa này có thể được tìm thấy trong một thư mục khác với thư mục hiển thị bên dưới, hãy nhập đường dẫn chính xác hoặc nhấp Duyệt.
PathLabel=&Đường dẫn:
FileNotInDir2=Tệp "%1" không thể được định vị trong "%2". Vui lòng chèn đĩa chính xác hoặc chọn một thư mục khác.
SelectDirectoryLabel=Vui lòng chỉ định vị trí của đĩa tiếp theo.

; *** Installation phase messages
SetupAborted=Setup chưa hoàn thành.%n%nVui lòng khắc phục sự cố và chạy lại Setup.
EntryAbortRetryIgnore=Nhấp Thử lại để thử lại, Bỏ qua để tiếp tục dù sao, hoặc Hủy bỏ để hủy cài đặt.

; *** Installation status messages
StatusClosingApplications=Đang đóng các ứng dụng...
StatusCreateDirs=Đang tạo thư mục...
StatusExtractFiles=Đang giải nén tệp...
StatusCreateIcons=Đang tạo lối tắt...
StatusCreateIniEntries=Đang tạo mục INI...
StatusCreateRegistryEntries=Đang tạo mục registry...
StatusRegisterFiles=Đang đăng ký tệp...
StatusSavingUninstall=Đang lưu thông tin gỡ cài đặt...
StatusRunProgram=Đang hoàn thành cài đặt...
StatusRestartingApplications=Đang khởi động lại các ứng dụng...
StatusRollback=Đang khôi phục các thay đổi...

; *** Misc. errors
ErrorInternal=Lỗi nội bộ: %1
ErrorFunctionFailedNoCode=%1 thất bại
ErrorFunctionFailed=%1 thất bại; mã %2
ErrorFunctionFailedWithMessage=%1 thất bại; mã %2.%n%3
ErrorExecutingProgram=Không thể thực thi tệp:%n%1

; *** Registry errors
ErrorRegOpenKey=Lỗi mở khóa registry:%n%1\%2
ErrorRegCreateKey=Lỗi tạo khóa registry:%n%1\%2
ErrorRegWriteKey=Lỗi ghi khóa registry:%n%1\%2

; *** INI errors
ErrorIniEntry=Lỗi tạo mục INI trong tệp "%1".

; *** File copying errors
FileAbortRetryIgnore=Nhấp Thử lại để thử lại, Bỏ qua để bỏ qua tệp này (không khuyến nghị), hoặc Hủy bỏ để hủy cài đặt.
FileAbortRetryIgnore2=Nhấp Thử lại để thử lại, Bỏ qua để tiếp tục dù sao (không khuyến nghị), hoặc Hủy bỏ để hủy cài đặt.
SourceIsCorrupted=Tệp nguồn bị hỏng
SourceDoesntExist=Tệp nguồn "%1" không tồn tại
ExistingFileReadOnly=Tệp hiện có được đánh dấu là chỉ đọc.%n%nNhấp Thử lại để xóa thuộc tính chỉ đọc và thử lại, Bỏ qua để bỏ qua tệp này, hoặc Hủy bỏ để hủy cài đặt.
ErrorReadingExistingDest=Đã xảy ra lỗi khi cố gắng đọc tệp hiện có:
FileExists=Tệp đã tồn tại.%n%nBạn có muốn Setup ghi đè lên nó không?
ExistingFileNewer=Tệp hiện có mới hơn tệp mà Setup đang cố gắng cài đặt. Bạn nên giữ tệp hiện có.%n%nBạn có muốn giữ tệp hiện có không?
ErrorChangingAttr=Đã xảy ra lỗi khi cố gắng thay đổi thuộc tính của tệp hiện có:
ErrorCreatingTemp=Đã xảy ra lỗi khi cố gắng tạo tệp trong thư mục đích:
ErrorReadingSource=Đã xảy ra lỗi khi cố gắng đọc tệp nguồn:
ErrorCopying=Đã xảy ra lỗi khi cố gắng sao chép tệp:
ErrorReplacingExistingFile=Đã xảy ra lỗi khi cố gắng thay thế tệp hiện có:
ErrorRestartReplace=RestartReplace thất bại:
ErrorRenamingTemp=Đã xảy ra lỗi khi cố gắng đổi tên tệp trong thư mục đích:
ErrorRegisterServer=Không thể đăng ký DLL/OCX: %1
ErrorRegSvr32Failed=RegSvr32 thất bại với mã thoát %1
ErrorRegisterTypeLib=Không thể đăng ký thư viện loại: %1

; *** Uninstall display name markings
UninstallDisplayNameMark=%1 (%2)
UninstallDisplayNameMarks=%1 (%2, %3)
UninstallDisplayNameMark32Bit=32-bit
UninstallDisplayNameMark64Bit=64-bit
UninstallDisplayNameMarkAllUsers=Tất cả người dùng
UninstallDisplayNameMarkCurrentUser=Người dùng hiện tại

; *** Post-installation errors
ErrorOpeningReadme=Đã xảy ra lỗi khi cố gắng mở tệp README.
ErrorRestartingComputer=Setup không thể khởi động lại máy tính. Vui lòng thực hiện điều này thủ công.

; *** Uninstaller messages
UninstallNotFound=Tệp "%1" không tồn tại. Không thể gỡ cài đặt.
UninstallOpenError=Tệp "%1" không thể được mở. Không thể gỡ cài đặt
UninstallUnsupportedVer=Tệp nhật ký gỡ cài đặt "%1" ở định dạng không được nhận dạng bởi phiên bản trình gỡ cài đặt này. Không thể gỡ cài đặt
UninstallUnknownEntry=Một mục không xác định (%1) đã được gặp trong nhật ký gỡ cài đặt
ConfirmUninstall=Bạn có chắc chắn muốn hoàn toàn xóa %1 và tất cả các thành phần của nó không?
UninstallOnlyOnWin64=Cài đặt này chỉ có thể được gỡ cài đặt trên Windows 64-bit.
OnlyAdminCanUninstall=Cài đặt này chỉ có thể được gỡ cài đặt bởi người dùng có đặc quyền quản trị.
UninstallStatusLabel=Vui lòng đợi trong khi %1 được xóa khỏi máy tính của bạn.
UninstalledAll=%1 đã được xóa thành công khỏi máy tính của bạn.
UninstalledMost=Gỡ cài đặt %1 hoàn tất.%n%nMột số phần tử không thể được xóa. Chúng có thể được xóa thủ công.
UninstalledAndNeedsRestart=Để hoàn thành việc gỡ cài đặt %1, máy tính của bạn phải được khởi động lại.%n%nBạn có muốn khởi động lại ngay bây giờ không?
UninstallDataCorrupted=Tệp "%1" bị hỏng. Không thể gỡ cài đặt

; *** Uninstallation phase messages
ConfirmDeleteSharedFileTitle=Xóa tệp được chia sẻ?
ConfirmDeleteSharedFile2=Hệ thống cho biết tệp được chia sẻ sau đây không còn được sử dụng bởi bất kỳ chương trình nào. Bạn có muốn Gỡ cài đặt xóa tệp được chia sẻ này không?%n%nNếu bất kỳ chương trình nào vẫn đang sử dụng tệp này và nó bị xóa, những chương trình đó có thể không hoạt động đúng cách. Nếu bạn không chắc chắn, hãy chọn Không. Việc để lại tệp trên hệ thống của bạn sẽ không gây hại.
SharedFileNameLabel=Tên tệp:
SharedFileLocationLabel=Vị trí:
WizardUninstalling=Trạng thái gỡ cài đặt
StatusUninstalling=Đang gỡ cài đặt %1...

; *** Shutdown block reasons
ShutdownBlockReasonInstallingApp=Đang cài đặt %1.
ShutdownBlockReasonUninstallingApp=Đang gỡ cài đặt %1.

; The custom messages below aren't used by Setup itself, but if you make
; use of them in your scripts, you'll want to translate them.

[CustomMessages]

BeveledLabel=
CreateDesktopIcon=Tạo biểu tượng &desktop
CreateQuickLaunchIcon=Tạo biểu tượng &Quick Launch
ProgramOnTheWeb=%1 trên Web
UninstallProgram=Gỡ cài đặt %1
LaunchProgram=Khởi chạy %1
AssocFileExtension=&Liên kết %1 với phần mở rộng tệp %2
AssocingFileExtension=Đang liên kết %1 với phần mở rộng tệp %2...
AutoStartProgramGroupDescription=Khởi động:
AutoStartProgram=Tự động khởi động %1
AddonHostProgramNotFound=%1 không thể được định vị trong thư mục bạn đã chọn.%n%nBạn có muốn tiếp tục dù sao không?