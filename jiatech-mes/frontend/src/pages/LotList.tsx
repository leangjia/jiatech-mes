import { useEffect } from 'react';
import { Table, Button, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useSearch } from '@/hooks/useMesApi';
import type { MesLot } from '@/types/mes';

function LotList() {
  const { data, loading, total, search } = useSearch<MesLot>('mes.lot');

  useEffect(() => {
    search({ page: 1, pageSize: 20 });
  }, [search]);

  const columns = [
    {
      title: 'Lot Number',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'State',
      dataIndex: 'state',
      key: 'state',
    },
    {
      title: 'Quantity',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      render: (value: number) => `${value || 0}%`,
    },
    {
      title: 'Action',
      key: 'action',
      render: () => (
        <Space>
          <Button size="small">View</Button>
          <Button size="small" type="primary">
            Track In
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
            Create Lot
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
          showTotal: (t) => `Total ${t} lots`,
        }}
      />
    </div>
  );
}

export default LotList;
