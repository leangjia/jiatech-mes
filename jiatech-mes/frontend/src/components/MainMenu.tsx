import { Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';

const menuItems = [
  {
    key: '/dashboard',
    label: 'Dashboard',
  },
  {
    key: '/wip',
    label: 'WIP',
    children: [
      { key: '/wip/lots', label: 'Lots' },
      { key: '/wip/workorders', label: 'Work Orders' },
      { key: '/wip/routes', label: 'Routes' },
    ],
  },
  {
    key: '/mm',
    label: 'Material',
    children: [
      { key: '/mm/products', label: 'Products' },
      { key: '/mm/bom', label: 'BOM' },
      { key: '/mm/stock', label: 'Stock' },
    ],
  },
  {
    key: '/ras',
    label: 'Resources',
    children: [
      { key: '/ras/equipment', label: 'Equipment' },
      { key: '/ras/workcenters', label: 'Work Centers' },
    ],
  },
  {
    key: '/spc',
    label: 'SPC',
    children: [
      { key: '/spc/control', label: 'Control Charts' },
      { key: '/spc/jobs', label: 'SPC Jobs' },
      { key: '/spc/data', label: 'Data' },
    ],
  },
  {
    key: '/pms',
    label: 'Maintenance',
    children: [
      { key: '/pms/maintenance', label: 'Maintenance' },
      { key: '/pms/schedules', label: 'Schedules' },
    ],
  },
  {
    key: '/alm',
    label: 'Alarms',
    children: [
      { key: '/alm/alarms', label: 'Alarm List' },
      { key: '/alm/rules', label: 'Rules' },
    ],
  },
  {
    key: '/qms',
    label: 'Quality',
    children: [
      { key: '/qms/quality', label: 'Quality' },
      { key: '/qms/defects', label: 'Defects' },
      { key: '/qms/ncr', label: 'NCR' },
    ],
  },
];

function MainMenu() {
  const navigate = useNavigate();
  const location = useLocation();

  const selectedKey = location.pathname;

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Menu
      mode="inline"
      selectedKeys={[selectedKey]}
      defaultOpenKeys={['/wip', '/mm', '/ras', '/spc', '/qms']}
      items={menuItems}
      onClick={handleMenuClick}
      style={{ height: '100%', borderRight: 0 }}
    />
  );
}

export default MainMenu;
