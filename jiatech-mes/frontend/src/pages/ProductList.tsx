import { useEffect } from 'react';
import { Table, Button, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useSearch } from '@/hooks/useMesApi';
import type { MesProduct } from '@/types/mes';

function ProductList() {
  const { data, loading, total, search } = useSearch<MesProduct>('mes.product');

  useEffect(() => {
    search({ page: 1, pageSize: 20 });
  }, [search]);

  const columns = [
    {
      title: 'Product Code',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: 'Product Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
    },
    {
      title: 'Tracking',
      dataIndex: 'tracking',
      key: 'tracking',
    },
    {
      title: 'Action',
      key: 'action',
      render: () => (
        <Space>
          <Button size="small">View</Button>
          <Button size="small" type="primary">
            Create Lot
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
            Create Product
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
          showTotal: (t) => `Total ${t} products`,
        }}
      />
    </div>
  );
}

export default ProductList;
