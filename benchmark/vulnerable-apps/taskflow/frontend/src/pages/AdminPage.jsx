import PageWrapper from '../components/Layout/PageWrapper';
import UserTable from '../components/Admin/UserTable';

export default function AdminPage() {
  return (
    <PageWrapper title="Admin">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Users</h2>
      <UserTable />
    </PageWrapper>
  );
}
