import { useEffect } from 'react';
import { Table, Card, Statistic, Row, Col, Tag, Button, Tabs } from 'antd';
import { useSearch } from '@/hooks/useMesApi';
import type { MesModel } from '@/types/mes';

interface Ncr extends MesModel {
  name: string;
  code: string;
  defect_id: number;
  lot_id: number;
  product_id: number;
  quantity: number;
  severity: 'minor' | 'major' | 'critical';
  state: 'draft' | 'submitted' | 'in_review' | 'approved' | 'rejected' | 'closed';
  origin: string;
  description: string;
  create_date: string;
}

interface Inspection extends MesModel {
  name: string;
  inspection_type: string;
  lot_id: number;
  state: 'pending' | 'in_progress' | 'passed' | 'failed';
  inspector: string;
  inspection_date: string;
  result: 'pass' | 'fail' | 'partial';
}

interface Defect extends MesModel {
  name: string;
  code: string;
  category_id: number;
  description: string;
}

function QmsPage() {
  const { data: ncrs, search: searchNcrs } = useSearch<Ncr>('mes.ncr');
  const { data: inspections, search: searchInspections } = useSearch<Inspection>('mes.inspection');
  const { data: defects, search: searchDefects } = useSearch<Defect>('mes.defect');

  useEffect(() => {
    searchNcrs({ page: 1, pageSize: 10 });
    searchInspections({ page: 1, pageSize: 10 });
    searchDefects({ page: 1, pageSize: 10 });
  }, [searchNcrs, searchInspections, searchDefects]);

  const getSeverityColor = (s: string) => {
    switch (s) {
      case 'critical': return 'red';
      case 'major': return 'orange';
      case 'minor': return 'blue';
      default: return 'default';
    }
  };

  const getStateColor = (s: string) => {
    switch (s) {
      case 'draft': return 'default';
      case 'submitted': return 'blue';
      case 'in_review': return 'orange';
      case 'approved': return 'green';
      case 'rejected': return 'red';
      case 'closed': return 'grey';
      case 'pending': return 'default';
      case 'in_progress': return 'blue';
      case 'passed': return 'green';
      case 'failed': return 'red';
      default: return 'default';
    }
  };

  const ncrColumns = [
    { title: 'Code', dataIndex: 'code', key: 'code' },
    { title: 'Description', dataIndex: 'description', key: 'description', ellipsis: true },
    { title: 'Lot', dataIndex: 'lot_id', key: 'lot_id' },
    { title: 'Qty', dataIndex: 'quantity', key: 'quantity' },
    { title: 'Severity', dataIndex: 'severity', key: 'severity',
      render: (s: string) => <Tag color={getSeverityColor(s)}>{s}</Tag> },
    { title: 'State', dataIndex: 'state', key: 'state',
      render: (s: string) => <Tag color={getStateColor(s)}>{s}</Tag> },
    { title: 'Date', dataIndex: 'create_date', key: 'create_date' },
  ];

  const inspectionColumns = [
    { title: 'Inspection', dataIndex: 'name', key: 'name' },
    { title: 'Type', dataIndex: 'inspection_type', key: 'inspection_type' },
    { title: 'Lot', dataIndex: 'lot_id', key: 'lot_id' },
    { title: 'Inspector', dataIndex: 'inspector', key: 'inspector' },
    { title: 'Result', dataIndex: 'result', key: 'result',
      render: (r: string) => <Tag color={r === 'pass' ? 'green' : r === 'fail' ? 'red' : 'orange'}>{r}</Tag> },
    { title: 'State', dataIndex: 'state', key: 'state',
      render: (s: string) => <Tag color={getStateColor(s)}>{s}</Tag> },
  ];

  const defectColumns = [
    { title: 'Code', dataIndex: 'code', key: 'code' },
    { title: 'Defect', dataIndex: 'name', key: 'name' },
    { title: 'Description', dataIndex: 'description', key: 'description', ellipsis: true },
  ];

  const openNcrs = ncrs?.filter(n => n.state !== 'closed').length || 0;
  const failedInspections = inspections?.filter(i => i.state === 'failed').length || 0;
  const passRate = inspections?.length ? Math.round((inspections.filter(i => i.result === 'pass').length / inspections.length) * 100) : 0;

  const items = [
    {
      key: 'ncr',
      label: 'NCR List',
      children: (
        <Table columns={ncrColumns} dataSource={ncrs} rowKey="id" size="small" pagination={false} />
      ),
    },
    {
      key: 'inspection',
      label: 'Inspections',
      children: (
        <Table columns={inspectionColumns} dataSource={inspections} rowKey="id" size="small" pagination={false} />
      ),
    },
    {
      key: 'defect',
      label: 'Defects',
      children: (
        <Table columns={defectColumns} dataSource={defects} rowKey="id" size="small" pagination={false} />
      ),
    },
  ];

  return (
    <div>
      <h2>Quality Management</h2>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card><Statistic title="Open NCRs" value={openNcrs} valueStyle={{ color: openNcrs > 0 ? '#cf1322' : '#52c41a' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Failed Inspections" value={failedInspections} valueStyle={{ color: failedInspections > 0 ? '#cf1322' : '#52c41a' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Pass Rate" value={passRate} suffix="%" valueStyle={{ color: passRate >= 95 ? '#52c41a' : passRate >= 80 ? '#faad14' : '#cf1322' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Defects" value={defects?.length || 0} /></Card>
        </Col>
      </Row>
      <Card extra={<Button type="primary">New NCR</Button>}>
        <Tabs items={items} />
      </Card>
    </div>
  );
}

export default QmsPage;
