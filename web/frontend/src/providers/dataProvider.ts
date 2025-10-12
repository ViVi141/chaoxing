import { DataProvider } from '@refinedev/core';
import { axiosInstance } from './authProvider';

export const dataProvider: DataProvider = {
  getList: async ({ resource, pagination, filters, sorters }) => {
    const { current = 1, pageSize = 10 } = pagination ?? {};

    const query: any = {
      page: current,
      page_size: pageSize,
    };

    if (sorters && sorters.length > 0) {
      query._sort = sorters[0].field;
      query._order = sorters[0].order === 'asc' ? 'ASC' : 'DESC';
    }

    if (filters) {
      filters.forEach((filter) => {
        if ('field' in filter) {
          query[filter.field] = filter.value;
        }
      });
    }

    const response = await axiosInstance.get(`/${resource}`, { params: query });

    return {
      data: response.data.items || response.data.data || [],
      total: response.data.total || 0,
    };
  },

  getOne: async ({ resource, id }) => {
    const response = await axiosInstance.get(`/${resource}/${id}`);

    return {
      data: response.data,
    };
  },

  create: async ({ resource, variables }) => {
    const response = await axiosInstance.post(`/${resource}`, variables);

    return {
      data: response.data,
    };
  },

  update: async ({ resource, id, variables }) => {
    const response = await axiosInstance.put(`/${resource}/${id}`, variables);

    return {
      data: response.data,
    };
  },

  deleteOne: async ({ resource, id }) => {
    const response = await axiosInstance.delete(`/${resource}/${id}`);

    return {
      data: response.data,
    };
  },

  getApiUrl: () => 'http://localhost:8000/api',
};

