/*# ---------------------------------------------------------------------
# Copyright (c) 2018 TU Berlin, Communication Systems Group
# Written by Tobias Senst <senst@nue.tu-berlin.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------*/

#include <vector>
#include <deque>
#include <iostream>
#include <stdlib.h>
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
#include <boost/python/object.hpp>
#include <boost/python/list.hpp>

namespace np = boost::python::numpy;

class TrajectoryEstimator 
{
	public:

	TrajectoryEstimator(){};
	~TrajectoryEstimator(){}
	/*
	 *param points rows = Anzahl der Trajectorien, cols = ( Start index, End index + 1, Startpunkt(x), Startpunkt(y))
	*/
	boost::python::list run(boost::python::list pyOFFilenames, np::ndarray pyPoints, float scale, int verbose);
};

