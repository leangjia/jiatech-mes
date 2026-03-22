export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  total: number;
  page: number;
  pageSize: number;
}

export interface MesModel {
  id: number;
  name: string;
  create_date?: string;
  write_date?: string;
  create_uid?: number;
  write_uid?: number;
  active?: boolean;
  company_id?: number;
}

export interface MesLot extends MesModel {
  name: string;
  state: 'draft' | 'created' | 'in_progress' | 'held' | 'completed' | 'closed' | 'scrapped';
  product_id: number;
  product_name?: string;
  quantity: number;
  uom_id: number;
  route_id?: number;
  bom_id?: number;
  progress?: number;
}

export interface MesProduct extends MesModel {
  name: string;
  code: string;
  type: 'stockable' | 'consumable' | 'service';
  uom_id: number;
  tracking: 'none' | 'lot' | 'serial';
  categ_id?: number;
}

export interface MesEquipment extends MesModel {
  name: string;
  code: string;
  category_id: number;
  state_id: number;
  location?: string;
  serial_number?: string;
}

export interface MesWorkorder extends MesModel {
  name: string;
  lot_id: number;
  product_id: number;
  state: 'pending' | 'ready' | 'in_progress' | 'done' | 'blocked';
  workcenter_id?: number;
  operation_id?: number;
}

export interface SearchParams {
  page?: number;
  pageSize?: number;
  domain?: Array<[string, string, unknown]>;
  fields?: string[];
  order?: string;
}
