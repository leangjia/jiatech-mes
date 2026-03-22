import { useEffect } from 'react';
import { Table, Button, Space, Tag } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useSearch } from '@/hooks/useMesApi';
import type { MesEquipment } from '@/types/mes';

function EquipmentList() {
  const { data, loading, total, search } = useSearch<MesEquipment>('mes.equipment');

  useEffect(() => {
    search({ page: 1, pageSize: 20 });
  }, [search]);

  const getStateColor = (state: string) => {
    switch (state) {
      case 'running':
        return 'green';
      case 'idle':
        return 'orange';
      case 'maintenance':
        return 'blue';
      case 'broken':
        return 'red';
      default:
        return 'default';
    }
  };

  const columns = [
    {
      title: 'Equipment Code',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: 'Equipment Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Location',
      dataIndex: 'location',
      key: 'location',
    },
    {
      title: 'Serial Number',
      dataIndex: 'serial_number',
      key: 'serial_number',
    },
    {
      title: 'State',
      key: 'state',
      render: () => <Tag color={getStateColor('running')}>Running</Tag>,
    },
    {
      title: 'Action',
      key: 'action',
      render: () => (
        <Space>
          <Button size="small">View</Button>
          <Button size="small" type="primary">
            Monitor
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Button type="primary" icon={<PlusOutlined />}>
            Add Equipment
          </Button>
          <Button onClick={() => search({ page: 1, pageSize: 20 })}>
            Refresh
          </Button>
        </Space>
      </div>
      <Table
        columns={columns}
        dataSource={data}
        loading={loading}
        rowKey="id"
        pagination={{
          total,
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (t) => `Total ${t} equipment`,
        }}
      />
    </div>
  );
}

export default EquipmentList;
