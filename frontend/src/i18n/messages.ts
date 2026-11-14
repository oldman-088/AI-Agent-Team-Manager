const en = {
  language: 'Language', eyebrow: 'AATM · LOCAL CONTROL CENTER', title: 'Team workspace', subtitle: 'A foundation for managing AI engineering teams.',
  system: 'System status', backend: 'Backend and database', ready: 'Ready', checking: 'Checking…', notReady: 'Not ready',
  refresh: 'Refresh data', readiness: 'Readiness indicates database connectivity only; it does not validate migrations or production security.',
  apiToken: 'Local API access token', applyToken: 'Apply token or clear', tokenHelp: 'Optional shared token if configured on the backend; never enter a provider API key here. Kept only in this tab memory; blank clears it.', tokenSet: 'A token is held in memory; access is not verified by this message.', tokenUnset: 'No API token is held in memory; the backend may require one.',
  projects: 'Projects', projectsHelp: 'Manage basic project records in the configured database.', projectName: 'Project name', description: 'Description',
  createProject: 'Create project', saving: 'Saving…', noProjects: 'No projects loaded.',
  agents: 'Agent configurations', agentsHelp: 'These are configuration records only. No agent process or lifecycle is implemented.',
  agentName: 'Agent name', role: 'Role', project: 'Project', unassigned: 'Unassigned', createAgent: 'Create configuration',
  noAgents: 'No agent configurations loaded.', noExecution: 'Agent process lifecycle not implemented',
  tasks: 'Planning tasks', tasksHelp: 'Tasks and assignments are planning records only; execution is not implemented.',
  manualComplete: 'Mark complete manually', completeHelp: 'Manual completion is your assertion; it does not mean an agent ran.', completeError: 'Could not complete task. Check that its dependencies are completed.',
  selectProject: 'Select a project', taskTitle: 'Task title', createTask: 'Create task', noTasks: 'No tasks loaded.',
  details: 'Dependencies and readiness', selectTask: 'Select task', chooseTask: 'Choose a task', prerequisite: 'Prerequisite', choosePrerequisite: 'Choose a prerequisite', addDependency: 'Add dependency', removeDependency: 'Remove dependency', dependencies: 'Dependencies', noDependencies: 'No dependencies.', readyTask: 'Ready for manual completion', blockedTask: 'Not ready for manual completion', blockers: 'Incomplete prerequisites', snapshotHelp: 'Readiness is a snapshot; the server rechecks before completion. Choices include only the first 100 loaded tasks.', dependencyError: 'Could not load or change dependencies. Refresh and check for cycles, task status or concurrent changes.', loadingDetails: 'Loading task details…', taskId: 'Task ID',
  assignment: 'Planning assignment', assignmentHelp: 'A planning association only; this does not start an agent. Only the first 100 loaded agents are available. Assignments can be added or changed only while pending; removal is also allowed afterwards.', clearAssignment: 'Remove assignment', selectAgent: 'Assigned agent configuration', saveAssignment: 'Save assignment', assignmentError: 'Could not load or change the assignment. Check the agent project and task status.', assignedMissing: 'Assigned agent outside the loaded list',
  readyTasks: 'Ready planning tasks', readyTasksHelp: 'Snapshot of up to 100 pending tasks with completed prerequisites. It does not reserve or start work; refresh to update.', noReadyTasks: 'No ready tasks loaded.',
  runs: 'Text run history', runsHelp: 'Manual CLI text runs only. Success means a response was received, not that the task is completed. Heartbeat age is advisory, not proof of process health; refresh for changes. First 100 runs only.', noRuns: 'No runs loaded.', runsError: 'Could not load run history.', runRunning: 'Running or interrupted', runSucceeded: 'Response received', runUncertain: 'Outcome uncertain', runResolved: 'Manually resolved',
  heartbeatFresh: 'Recent heartbeat', heartbeatStale: 'Heartbeat stale', heartbeatUnknown: 'Heartbeat unknown', heartbeatNotRunning: 'Run not active',
  agentClaim: 'Recorded agent claim', agentClaimSelect: 'Inspect agent claim', agentClaimChoose: 'Choose an agent', agentClaimHelp: 'Snapshot of unresolved claims, not proof of process or provider status. No recorded claim does not prove an agent or remote request is stopped. Refresh to update.', agentClaimError: 'Could not inspect this agent claim.', agentClaimNone: 'No unresolved claim recorded.', agentRunId: 'Run ID',
  unresolvedRuns: 'Unresolved worker runs', unresolvedHelp: 'First 100 unresolved runs across projects, an advisory snapshot. A stale or missing heartbeat does not prove the worker or remote request stopped. Do not retry or release a claim without investigation.', unresolvedError: 'Could not inspect unresolved runs. Check the API token and backend.', noUnresolved: 'No unresolved runs found.',
  activity: 'Recent task activity', activityHelp: 'Metadata only; this is not a security audit log. Timestamps use database time.', noActivity: 'No activity loaded.',
  eventCreated: 'Task created', eventUpdated: 'Task updated', eventCancelled: 'Task cancelled', eventCompleted: 'Task completed manually', eventDeleted: 'Task deleted', eventDependencyAdded: 'Dependency added', eventDependencyRemoved: 'Dependency removed', eventAssigned: 'Task assigned for planning', eventUnassigned: 'Task unassigned', eventUnknown: 'Other activity',
  underConstruction: 'Under construction', limitations: 'Autonomous agent lifecycle and orchestration are not available in this dashboard; the manual text worker is a local CLI. Editing and deletion are available through the API only.',
  loadError: 'Could not load data. Check the API token, backend and database.', projectError: 'Could not create the project. Check the form and database.',
  agentError: 'Could not create the agent configuration. Check the form and database.', taskError: 'Could not create the task. Check the form and database.',
  planned: 'Planned', active: 'Active', paused: 'Paused', completed: 'Completed', archived: 'Archived', pending: 'Pending', cancelled: 'Cancelled', unknown: 'Unknown',
} as const;

type MessageKey = keyof typeof en;
export type Locale = 'en' | 'ar' | 'fa';
type Translations = Record<MessageKey, string>;

const ar: Translations = {
  language: 'اللغة', eyebrow: 'AATM · مركز التحكم المحلي', title: 'مساحة عمل الفريق', subtitle: 'أساس لإدارة فرق هندسة الذكاء الاصطناعي.',
  system: 'حالة النظام', backend: 'الخادم وقاعدة البيانات', ready: 'جاهز', checking: 'جارٍ التحقق…', notReady: 'غير جاهز',
  refresh: 'تحديث البيانات', readiness: 'تشير الجاهزية إلى الاتصال بقاعدة البيانات فقط؛ ولا تتحقق من الترحيلات أو أمان بيئة الإنتاج.',
  apiToken: 'رمز وصول API المحلي', applyToken: 'تطبيق الرمز أو مسحه', tokenHelp: 'رمز مشترك اختياري إذا ضُبط في الخادم؛ لا تُدخل مفتاح المزوّد هنا. يُحفظ في ذاكرة هذه الصفحة فقط؛ الحقل الفارغ يمسحه.', tokenSet: 'الرمز محفوظ في الذاكرة؛ هذه الرسالة لا تثبت صلاحية الوصول.', tokenUnset: 'لا يوجد رمز في الذاكرة؛ قد يتطلب الخادم رمزًا.',
  projects: 'المشاريع', projectsHelp: 'إدارة سجلات المشاريع الأساسية في قاعدة البيانات المُعدّة.', projectName: 'اسم المشروع', description: 'الوصف',
  createProject: 'إنشاء مشروع', saving: 'جارٍ الحفظ…', noProjects: 'لا توجد مشاريع محمّلة.',
  agents: 'إعدادات الوكلاء', agentsHelp: 'هذه سجلات إعدادات فقط؛ لم يُنفّذ تشغيل الوكلاء أو دورة حياتهم.',
  agentName: 'اسم الوكيل', role: 'الدور', project: 'المشروع', unassigned: 'غير مُسند', createAgent: 'إنشاء إعداد',
  noAgents: 'لا توجد إعدادات وكلاء محمّلة.', noExecution: 'التنفيذ غير مطبّق',
  tasks: 'المهام التخطيطية', tasksHelp: 'هذه سجلات للتخطيط فقط؛ التبعيات قابلة للتعديل عبر API، لكن الإسناد والتنفيذ غير مطبّقين.',
  manualComplete: 'تحديد المهمة كمكتملة يدويًا', completeHelp: 'الإكمال اليدوي تأكيد منك، ولا يعني أن وكيلًا نفّذ المهمة.', completeError: 'تعذّر إكمال المهمة. تحقق من إكمال تبعياتها.',
  selectProject: 'اختر مشروعًا', taskTitle: 'عنوان المهمة', createTask: 'إنشاء مهمة', noTasks: 'لا توجد مهام محمّلة.',
  details: 'التبعيات والجاهزية', selectTask: 'اختر مهمة', chooseTask: 'اختر مهمة', prerequisite: 'المهمة المطلوبة مسبقًا', choosePrerequisite: 'اختر مهمة مطلوبة', addDependency: 'إضافة تبعية', removeDependency: 'إزالة التبعية', dependencies: 'التبعيات', noDependencies: 'لا توجد تبعيات.', readyTask: 'جاهزة للإكمال اليدوي', blockedTask: 'غير جاهزة للإكمال اليدوي', blockers: 'المهام المطلوبة غير المكتملة', snapshotHelp: 'الجاهزية لقطة مؤقتة؛ يعيد الخادم التحقق قبل الإكمال. الخيارات من أول 100 مهمة محمّلة فقط.', dependencyError: 'تعذر تحميل التبعيات أو تغييرها. حدّث البيانات وتحقق من الدورات وحالة المهمة والتغييرات المتزامنة.', loadingDetails: 'جارٍ تحميل تفاصيل المهمة…', taskId: 'رقم المهمة',
  assignment: 'الإسناد التخطيطي', assignmentHelp: 'إسناد للتخطيط فقط ولا يشغّل الوكيل. تتاح أول 100 إعداد وكيل محمّل فقط. الإضافة والتغيير للمهام المعلّقة فقط، والإزالة متاحة بعدها أيضًا.', clearAssignment: 'إزالة الإسناد', selectAgent: 'إعداد الوكيل المسند', saveAssignment: 'حفظ الإسناد', assignmentError: 'تعذّر تحميل الإسناد أو تغييره. تحقق من مشروع الوكيل وحالة المهمة.', assignedMissing: 'الوكيل المسند خارج القائمة المحمّلة',
  readyTasks: 'المهام الجاهزة للتخطيط', readyTasksHelp: 'لقطة لما يصل إلى 100 مهمة معلّقة اكتملت متطلباتها. لا تحجز المهمة أو تشغّلها؛ حدّث البيانات لتجديدها.', noReadyTasks: 'لا توجد مهام جاهزة محمّلة.',
  runs: 'سجل التشغيل النصي', runsHelp: 'تشغيل نصي يدوي من سطر الأوامر فقط. النجاح يعني استلام رد وليس إكمال المهمة. عمر النبضة مؤشر تقريبي وليس إثباتًا لحياة العملية؛ حدّث البيانات. أول 100 محاولة فقط.', noRuns: 'لا توجد محاولات محمّلة.', runsError: 'تعذّر تحميل سجل التشغيل.', runRunning: 'قيد التشغيل أو متوقف', runSucceeded: 'تم استلام الرد', runUncertain: 'النتيجة غير مؤكدة', runResolved: 'حُلّت يدويًا',
  heartbeatFresh: 'نبضة حديثة', heartbeatStale: 'النبضة قديمة', heartbeatUnknown: 'النبضة غير معروفة', heartbeatNotRunning: 'المحاولة غير نشطة',
  agentClaim: 'حجز الوكيل المسجّل', agentClaimSelect: 'فحص حجز الوكيل', agentClaimChoose: 'اختر وكيلاً', agentClaimHelp: 'لقطة للحجوزات غير المحسومة وليست إثباتًا لحالة العملية أو المزوّد. غياب الحجز لا يثبت توقف الوكيل أو الطلب البعيد. حدّث البيانات للاطلاع على التغييرات.', agentClaimError: 'تعذر فحص حجز الوكيل.', agentClaimNone: 'لا يوجد حجز غير محسوم مسجّل.', agentRunId: 'معرّف التشغيل',
  unresolvedRuns: 'محاولات العامل غير المحسومة', unresolvedHelp: 'أول 100 محاولة غير محسومة عبر المشاريع، كلقطة إرشادية. لا تثبت النبضة القديمة أو المفقودة توقف العامل أو الطلب البعيد. لا تعِد المحاولة أو تحرّر الحجز قبل التحقيق.', unresolvedError: 'تعذر فحص المحاولات غير المحسومة. تحقق من رمز API والخادم.', noUnresolved: 'لم تُعثر على محاولات غير محسومة.',
  activity: 'أحداث المهام الأخيرة', activityHelp: 'بيانات وصفية فقط؛ هذا ليس سجل تدقيق أمني. التوقيت وفق قاعدة البيانات.', noActivity: 'لا توجد أحداث محمّلة.',
  eventCreated: 'أُنشئت مهمة', eventUpdated: 'عُدّلت مهمة', eventCancelled: 'أُلغيت مهمة', eventCompleted: 'أُكملت مهمة يدويًا', eventDeleted: 'حُذفت مهمة', eventDependencyAdded: 'أُضيفت تبعية', eventDependencyRemoved: 'أُزيلت تبعية', eventAssigned: 'أُسندت مهمة تخطيطيًا', eventUnassigned: 'أُلغي إسناد مهمة', eventUnknown: 'حدث آخر',
  underConstruction: 'قيد الإنشاء', limitations: 'تشغيل الوكلاء والمزوّدون والتنسيق غير متاحة في لوحة التحكم. التعديل والحذف متاحان عبر واجهة API فقط.',
  loadError: 'تعذّر تحميل البيانات. تحقق من رمز API والخادم وقاعدة البيانات.', projectError: 'تعذّر إنشاء المشروع. تحقق من النموذج وقاعدة البيانات.',
  agentError: 'تعذّر إنشاء إعداد الوكيل. تحقق من النموذج وقاعدة البيانات.', taskError: 'تعذّر إنشاء المهمة. تحقق من النموذج وقاعدة البيانات.',
  planned: 'مخطط', active: 'نشط', paused: 'متوقف مؤقتًا', completed: 'مكتمل', archived: 'مؤرشف', pending: 'معلّقة', cancelled: 'ملغاة', unknown: 'غير معروف',
};

const fa: Translations = {
  language: 'زبان', eyebrow: 'AATM · مرکز کنترل محلی', title: 'فضای کاری تیم', subtitle: 'زیربنایی برای مدیریت تیم‌های مهندسی هوش مصنوعی.',
  system: 'وضعیت سامانه', backend: 'سرور و پایگاه داده', ready: 'آماده', checking: 'در حال بررسی…', notReady: 'آماده نیست',
  refresh: 'به‌روزرسانی داده‌ها', readiness: 'آمادگی فقط اتصال پایگاه داده را نشان می‌دهد و مهاجرت‌ها یا امنیت محیط تولید را بررسی نمی‌کند.',
  apiToken: 'رمز دسترسی API محلی', applyToken: 'اعمال یا پاک کردن رمز', tokenHelp: 'رمز مشترک اختیاری در صورت تنظیم روی سرور؛ کلید ارائه‌دهنده را اینجا وارد نکنید. فقط در حافظه این صفحه نگهداری می‌شود؛ مقدار خالی آن را پاک می‌کند.', tokenSet: 'رمز در حافظه است؛ این پیام تأیید دسترسی نیست.', tokenUnset: 'رمزی در حافظه نیست؛ ممکن است سرور رمز بخواهد.',
  projects: 'پروژه‌ها', projectsHelp: 'مدیریت اطلاعات پایه پروژه‌ها در پایگاه داده تنظیم‌شده.', projectName: 'نام پروژه', description: 'توضیحات',
  createProject: 'ایجاد پروژه', saving: 'در حال ذخیره…', noProjects: 'پروژه‌ای بارگذاری نشده است.',
  agents: 'پیکربندی عامل‌ها', agentsHelp: 'این‌ها فقط رکوردهای پیکربندی هستند؛ اجرای عامل و چرخه عمر آن پیاده‌سازی نشده است.',
  agentName: 'نام عامل', role: 'نقش', project: 'پروژه', unassigned: 'بدون تخصیص', createAgent: 'ایجاد پیکربندی',
  noAgents: 'پیکربندی عاملی بارگذاری نشده است.', noExecution: 'چرخه عمر عامل پیاده‌سازی نشده است',
  tasks: 'وظایف برنامه‌ریزی', tasksHelp: 'این‌ها فقط رکوردهای برنامه‌ریزی هستند؛ تخصیص فقط برای برنامه‌ریزی است و اجرا پیاده‌سازی نشده است.',
  manualComplete: 'علامت‌گذاری دستی به عنوان تکمیل‌شده', completeHelp: 'تکمیل دستی تأیید شماست و به معنی اجرای عامل نیست.', completeError: 'تکمیل وظیفه ممکن نشد. تکمیل وابستگی‌ها را بررسی کنید.',
  selectProject: 'پروژه‌ای انتخاب کنید', taskTitle: 'عنوان وظیفه', createTask: 'ایجاد وظیفه', noTasks: 'وظیفه‌ای بارگذاری نشده است.',
  details: 'وابستگی‌ها و آمادگی', selectTask: 'انتخاب وظیفه', chooseTask: 'وظیفه‌ای انتخاب کنید', prerequisite: 'پیش‌نیاز', choosePrerequisite: 'پیش‌نیازی انتخاب کنید', addDependency: 'افزودن وابستگی', removeDependency: 'حذف وابستگی', dependencies: 'وابستگی‌ها', noDependencies: 'وابستگی وجود ندارد.', readyTask: 'آماده تکمیل دستی', blockedTask: 'برای تکمیل دستی آماده نیست', blockers: 'پیش‌نیازهای تکمیل‌نشده', snapshotHelp: 'آمادگی لحظه‌ای است؛ سرور پیش از تکمیل دوباره بررسی می‌کند. گزینه‌ها فقط از ۱۰۰ وظیفه اول بارگذاری‌شده هستند.', dependencyError: 'بارگذاری یا تغییر وابستگی ناموفق بود. داده‌ها، چرخه‌ها و وضعیت وظیفه را بررسی کنید.', loadingDetails: 'در حال بارگذاری جزئیات وظیفه…', taskId: 'شناسه وظیفه',
  assignment: 'تخصیص برنامه‌ریزی', assignmentHelp: 'فقط برای برنامه‌ریزی است و عامل را اجرا نمی‌کند. فقط ۱۰۰ پیکربندی اول بارگذاری‌شده در دسترس‌اند. افزودن و تغییر فقط برای وظایف در انتظار و حذف پس از آن نیز مجاز است.', clearAssignment: 'حذف تخصیص', selectAgent: 'پیکربندی عامل تخصیص‌یافته', saveAssignment: 'ذخیره تخصیص', assignmentError: 'بارگذاری یا تغییر تخصیص ناموفق بود. پروژه عامل و وضعیت وظیفه را بررسی کنید.', assignedMissing: 'عامل تخصیص‌یافته خارج از فهرست بارگذاری‌شده است',
  readyTasks: 'وظایف آماده برنامه‌ریزی', readyTasksHelp: 'نمای لحظه‌ای حداکثر ۱۰۰ وظیفه در انتظار با پیش‌نیازهای تکمیل‌شده است. کاری رزرو یا اجرا نمی‌شود؛ برای به‌روزرسانی داده‌ها را تازه کنید.', noReadyTasks: 'وظیفه آماده‌ای بارگذاری نشده است.',
  runs: 'تاریخچه اجرای متنی', runsHelp: 'فقط اجرای متنی دستی از خط فرمان. موفقیت یعنی پاسخ دریافت شده، نه تکمیل وظیفه. وضعیت ضربان تقریبی است و سلامت فرایند را ثابت نمی‌کند؛ داده‌ها را تازه کنید. فقط ۱۰۰ اجرای اول.', noRuns: 'اجرایی بارگذاری نشده است.', runsError: 'بارگذاری تاریخچه اجرا ناموفق بود.', runRunning: 'در حال اجرا یا متوقف‌شده', runSucceeded: 'پاسخ دریافت شد', runUncertain: 'نتیجه نامشخص', runResolved: 'دستی تعیین تکلیف شد',
  heartbeatFresh: 'ضربان اخیر', heartbeatStale: 'ضربان قدیمی', heartbeatUnknown: 'ضربان نامشخص', heartbeatNotRunning: 'اجرا فعال نیست',
  agentClaim: 'رزرو ثبت‌شده عامل', agentClaimSelect: 'بررسی رزرو عامل', agentClaimChoose: 'انتخاب عامل', agentClaimHelp: 'نمایی از رزروهای تعیین‌تکلیف‌نشده است، نه اثبات وضعیت فرایند یا ارائه‌دهنده. نبود رزرو ثابت نمی‌کند که عامل یا درخواست راه دور متوقف است. برای تغییرات تازه‌سازی کنید.', agentClaimError: 'بررسی رزرو عامل ناموفق بود.', agentClaimNone: 'رزرو تعیین‌تکلیف‌نشده‌ای ثبت نشده است.', agentRunId: 'شناسه اجرا',
  unresolvedRuns: 'اجراهای تعیین‌تکلیف‌نشده', unresolvedHelp: '۱۰۰ اجرای نخست در پروژه‌ها، تنها یک نمای راهنماست. ضربان قدیمی یا غایب ثابت نمی‌کند که عامل یا درخواست راه دور متوقف شده است. پیش از بررسی، تلاش را تکرار یا رزرو را آزاد نکنید.', unresolvedError: 'بررسی اجراهای تعیین‌تکلیف‌نشده ناموفق بود. رمز API و سرور را بررسی کنید.', noUnresolved: 'اجرای تعیین‌تکلیف‌نشده‌ای یافت نشد.',
  activity: 'فعالیت اخیر وظایف', activityHelp: 'فقط فراداده؛ این گزارش ممیزی امنیتی نیست. زمان‌ها مطابق پایگاه داده‌اند.', noActivity: 'فعالیتی بارگذاری نشده است.',
  eventCreated: 'وظیفه ایجاد شد', eventUpdated: 'وظیفه ویرایش شد', eventCancelled: 'وظیفه لغو شد', eventCompleted: 'وظیفه دستی تکمیل شد', eventDeleted: 'وظیفه حذف شد', eventDependencyAdded: 'وابستگی افزوده شد', eventDependencyRemoved: 'وابستگی حذف شد', eventAssigned: 'وظیفه برای برنامه‌ریزی تخصیص یافت', eventUnassigned: 'تخصیص وظیفه حذف شد', eventUnknown: 'فعالیت دیگر',
  underConstruction: 'در دست ساخت', limitations: 'اجرای عامل‌ها، ارائه‌دهندگان و هماهنگی در این داشبورد در دسترس نیستند. ویرایش و حذف فقط از طریق API در دسترس است.',
  loadError: 'بارگذاری داده‌ها ناموفق بود. رمز API، سرور و پایگاه داده را بررسی کنید.', projectError: 'ایجاد پروژه ناموفق بود. فرم و پایگاه داده را بررسی کنید.',
  agentError: 'ایجاد پیکربندی عامل ناموفق بود. فرم و پایگاه داده را بررسی کنید.', taskError: 'ایجاد وظیفه ناموفق بود. فرم و پایگاه داده را بررسی کنید.',
  planned: 'برنامه‌ریزی‌شده', active: 'فعال', paused: 'متوقف', completed: 'تکمیل‌شده', archived: 'بایگانی‌شده', pending: 'در انتظار', cancelled: 'لغوشده', unknown: 'نامشخص',
};

export const messages: Record<Locale, Translations> = {en, ar, fa};
export const direction = (locale: Locale): 'ltr' | 'rtl' => locale === 'en' ? 'ltr' : 'rtl';
export function statusLabel(locale: Locale, status: string): string {
  const labels: Record<string, MessageKey> = {planned: 'planned', active: 'active', paused: 'paused', completed: 'completed', archived: 'archived', pending: 'pending', cancelled: 'cancelled'};
  return messages[locale][labels[status] ?? 'unknown'];
}

export function eventLabel(locale: Locale, event: string): string {
  const labels: Record<string, MessageKey> = {
    'task.created': 'eventCreated', 'task.updated': 'eventUpdated', 'task.cancelled': 'eventCancelled',
    'task.completed_manual': 'eventCompleted', 'task.deleted': 'eventDeleted',
    'dependency.added': 'eventDependencyAdded', 'dependency.removed': 'eventDependencyRemoved', 'task.assigned': 'eventAssigned', 'task.unassigned': 'eventUnassigned',
  };
  return messages[locale][labels[event] ?? 'eventUnknown'];
}
