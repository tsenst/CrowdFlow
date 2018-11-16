/** 
 * \file python_module.cpp
 * \brief Python interface
 * \date 23.03.2018
 * \author Tobias Senst
 */
 

#include <vector>
#include <deque>
#include <iostream>
#include <stdlib.h> 
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
#include <boost/python/stl_iterator.hpp>
#include <boost/multiprecision/cpp_int.hpp>
#include <boost/multiprecision/number.hpp>
#include <iostream>
#include "trajectory_module.h"

namespace np = boost::python::numpy;
namespace py = boost::python;

BOOST_PYTHON_MODULE (pytrajectory)
{
	Py_Initialize();
	np::initialize();

	
	py::class_<TrajectoryEstimator>("TrajectoryEstimator")
		 .def("run",&TrajectoryEstimator::run)
		;
}

