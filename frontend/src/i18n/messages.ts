const en = {
  language: 'Language', eyebrow: 'AATM · LOCAL CONTROL CENTER', title: 'Team workspace', subtitle: 'A foundation for managing AI engineering teams.',
  system: 'System status', backend: 'Backend and database', ready: 'Ready', checking: 'Checking…', notReady: 'Not ready',
  refresh: 'Refresh data', readiness: 'Readiness indicates database connectivity only; it does not validate migrations or production security.',
  projects: 'Projects', projectsHelp: 'Manage basic project records in the configured database.', projectName: 'Project name', description: 'Description',
  createProject: 'Create project', saving: 'Saving…', noProjects: 'No projects loaded.',
  agents: 'Agent configurations', agentsHelp: 'These are configuration records only. No agent process or lifecycle is implemented.',
  agentName: 'Agent name', role: 'Role', project: 'Project', unassigned: 'Unassigned', createAgent: 'Create configuration',
  noAgents: 'No agent configurations loaded.', noExecution: 'Execution not implemented',
  tasks: 'Planning tasks', tasksHelp: 'Tasks are planning records only; agent assignment, dependencies and execution are not implemented.',
  selectProject: 'Select a project', taskTitle: 'Task title', createTask: 'Create task', noTasks: 'No tasks loaded.',
  underConstruction: 'Under construction', limitations: 'Agent execution, providers and orchestration are not available in this dashboard. Editing and deletion are available through the API only.',
  loadError: 'Could not load data. Check the backend and database.', projectError: 'Could not create the project. Check the form and database.',
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
  projects: 'المشاريع', projectsHelp: 'إدارة سجلات المشاريع الأساسية في قاعدة البيانات المُعدّة.', projectName: 'اسم المشروع', description: 'الوصف',
  createProject: 'إنشاء مشروع', saving: 'جارٍ الحفظ…', noProjects: 'لا توجد مشاريع محمّلة.',
  agents: 'إعدادات الوكلاء', agentsHelp: 'هذه سجلات إعدادات فقط؛ لم يُنفّذ تشغيل الوكلاء أو دورة حياتهم.',
  agentName: 'اسم الوكيل', role: 'الدور', project: 'المشروع', unassigned: 'غير مُسند', createAgent: 'إنشاء إعداد',
  noAgents: 'لا توجد إعدادات وكلاء محمّلة.', noExecution: 'التنفيذ غير مطبّق',
  tasks: 'المهام التخطيطية', tasksHelp: 'هذه سجلات للتخطيط فقط؛ لم تُنفّذ التبعيات أو إسناد المهام أو تنفيذها.',
  selectProject: 'اختر مشروعًا', taskTitle: 'عنوان المهمة', createTask: 'إنشاء مهمة', noTasks: 'لا توجد مهام محمّلة.',
  underConstruction: 'قيد الإنشاء', limitations: 'تشغيل الوكلاء والمزوّدون والتنسيق غير متاحة في لوحة التحكم. التعديل والحذف متاحان عبر واجهة API فقط.',
  loadError: 'تعذّر تحميل البيانات. تحقق من الخادم وقاعدة البيانات.', projectError: 'تعذّر إنشاء المشروع. تحقق من النموذج وقاعدة البيانات.',
  agentError: 'تعذّر إنشاء إعداد الوكيل. تحقق من النموذج وقاعدة البيانات.', taskError: 'تعذّر إنشاء المهمة. تحقق من النموذج وقاعدة البيانات.',
  planned: 'مخطط', active: 'نشط', paused: 'متوقف مؤقتًا', completed: 'مكتمل', archived: 'مؤرشف', pending: 'معلّقة', cancelled: 'ملغاة', unknown: 'غير معروف',
};

const fa: Translations = {
  language: 'زبان', eyebrow: 'AATM · مرکز کنترل محلی', title: 'فضای کاری تیم', subtitle: 'زیربنایی برای مدیریت تیم‌های مهندسی هوش مصنوعی.',
  system: 'وضعیت سامانه', backend: 'سرور و پایگاه داده', ready: 'آماده', checking: 'در حال بررسی…', notReady: 'آماده نیست',
  refresh: 'به‌روزرسانی داده‌ها', readiness: 'آمادگی فقط اتصال پایگاه داده را نشان می‌دهد و مهاجرت‌ها یا امنیت محیط تولید را بررسی نمی‌کند.',
  projects: 'پروژه‌ها', projectsHelp: 'مدیریت اطلاعات پایه پروژه‌ها در پایگاه داده تنظیم‌شده.', projectName: 'نام پروژه', description: 'توضیحات',
  createProject: 'ایجاد پروژه', saving: 'در حال ذخیره…', noProjects: 'پروژه‌ای بارگذاری نشده است.',
  agents: 'پیکربندی عامل‌ها', agentsHelp: 'این‌ها فقط رکوردهای پیکربندی هستند؛ اجرای عامل و چرخه عمر آن پیاده‌سازی نشده است.',
  agentName: 'نام عامل', role: 'نقش', project: 'پروژه', unassigned: 'بدون تخصیص', createAgent: 'ایجاد پیکربندی',
  noAgents: 'پیکربندی عاملی بارگذاری نشده است.', noExecution: 'اجرا پیاده‌سازی نشده است',
  tasks: 'وظایف برنامه‌ریزی', tasksHelp: 'این‌ها فقط رکوردهای برنامه‌ریزی هستند؛ تخصیص به عامل، وابستگی‌ها و اجرا پیاده‌سازی نشده‌اند.',
  selectProject: 'پروژه‌ای انتخاب کنید', taskTitle: 'عنوان وظیفه', createTask: 'ایجاد وظیفه', noTasks: 'وظیفه‌ای بارگذاری نشده است.',
  underConstruction: 'در دست ساخت', limitations: 'اجرای عامل‌ها، ارائه‌دهندگان و هماهنگی در این داشبورد در دسترس نیستند. ویرایش و حذف فقط از طریق API در دسترس است.',
  loadError: 'بارگذاری داده‌ها ناموفق بود. سرور و پایگاه داده را بررسی کنید.', projectError: 'ایجاد پروژه ناموفق بود. فرم و پایگاه داده را بررسی کنید.',
  agentError: 'ایجاد پیکربندی عامل ناموفق بود. فرم و پایگاه داده را بررسی کنید.', taskError: 'ایجاد وظیفه ناموفق بود. فرم و پایگاه داده را بررسی کنید.',
  planned: 'برنامه‌ریزی‌شده', active: 'فعال', paused: 'متوقف', completed: 'تکمیل‌شده', archived: 'بایگانی‌شده', pending: 'در انتظار', cancelled: 'لغوشده', unknown: 'نامشخص',
};

export const messages: Record<Locale, Translations> = {en, ar, fa};
export const direction = (locale: Locale): 'ltr' | 'rtl' => locale === 'en' ? 'ltr' : 'rtl';
export function statusLabel(locale: Locale, status: string): string {
  const labels: Record<string, MessageKey> = {planned: 'planned', active: 'active', paused: 'paused', completed: 'completed', archived: 'archived', pending: 'pending', cancelled: 'cancelled'};
  return messages[locale][labels[status] ?? 'unknown'];
}
