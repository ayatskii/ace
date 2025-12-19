import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import MainLayout from '../../components/layout/MainLayout';
import TestCard from '../../components/student/TestCard';
import { testsApi } from '../../api/tests';

export default function TestList() {
  const [filter, setFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Fetch tests from API
  const { data: tests, isLoading, error } = useQuery({
    queryKey: ['tests'],
    queryFn: () => testsApi.getAll(),
  });
  
  // Filter tests
  const filteredTests = tests?.data?.filter((test) => {
    const matchesType = filter === 'all' || test.test_type === filter;
    const matchesSearch = test.title.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  }) || [];
  
  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Browse Tests</h1>
          <p className="text-gray-600 mt-2">
            Choose from our collection of full-length IELTS mock tests
          </p>
        </div>
        
        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            {/* Search */}
            <div className="flex-1 max-w-md">
              <input
                type="text"
                placeholder="Search tests..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            
            {/* Filter Buttons */}
            <div className="flex space-x-2">
              <button
                onClick={() => setFilter('all')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition ${
                  filter === 'all'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All Tests
              </button>
              <button
                onClick={() => setFilter('academic')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition ${
                  filter === 'academic'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Academic
              </button>
              <button
                onClick={() => setFilter('general_training')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition ${
                  filter === 'general_training'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                General Training
              </button>
            </div>
          </div>
        </div>
        
        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600">Loading tests...</p>
          </div>
        )}
        
        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
            Failed to load tests. Please try again later.
          </div>
        )}
        
        {/* Tests Grid */}
        {!isLoading && !error && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredTests.length > 0 ? (
              filteredTests.map((test) => <TestCard key={test.id} test={test} />)
            ) : (
              <div className="col-span-2 text-center py-12">
                <p className="text-gray-500">No tests found matching your criteria.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
