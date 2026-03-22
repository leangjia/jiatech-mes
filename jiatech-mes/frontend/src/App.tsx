import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from 'antd';
import MainMenu from '@components/MainMenu';
import Dashboard from '@pages/Dashboard';
import LotList from '@pages/LotList';
import ProductList from '@pages/ProductList';
import EquipmentList from '@pages/EquipmentList';

const { Header, Content, Sider } = Layout;

function App() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px', color: '#fff' }}>
        <h1 style={{ color: '#fff', margin: 0, lineHeight: '64px' }}>Jia Tech MES</h1>
      </Header>
      <Layout>
        <Sider width={200} style={{ background: '#fff' }}>
          <MainMenu />
        </Sider>
        <Layout style={{ padding: '0 24px 24px' }}>
          <Content
            style={{
              background: '#fff',
              padding: 24,
              margin: 0,
              minHeight: 280,
            }}
          >
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/wip/lots" element={<LotList />} />
              <Route path="/mm/products" element={<ProductList />} />
              <Route path="/ras/equipment" element={<EquipmentList />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

export default App;
