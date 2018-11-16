#include <vector>
#include <deque>
#include <iostream>
#include <stdlib.h>
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
#include <boost/python/object.hpp>
#include <boost/python/list.hpp>
#include <boost/python/stl_iterator.hpp>
#include <boost/python/suite/indexing/map_indexing_suite.hpp>

namespace np = boost::python::numpy;

class TrajectoryEstimator 
{
	public:

	TrajectoryEstimator(){};
	~TrajectoryEstimator(){}
	//void python_set_parameter(boost::python::dict & param);
	/*
	 *param points rows = Anzahl der Trajectorien, cols = ( Start index, End index + 1, Startpunkt(x), Startpunkt(y))
	*/
	boost::python::list run(boost::python::list pyOFFilenames, np::ndarray pyPoints, float scale, int verbose);
	protected:
	//void parseString(std::string key, std::string val);
};

