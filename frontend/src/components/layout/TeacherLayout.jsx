import Header from './Header';
import TeacherSidebar from './TeacherSidebar';

export default function TeacherLayout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <TeacherSidebar />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
