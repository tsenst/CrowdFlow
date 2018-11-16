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
#include "opencv2/ximgproc.hpp" // for struct edge detection
#include "opencv2/optflow.hpp"
#include "trajectory_module.h"

namespace np = boost::python::numpy;
namespace py = boost::python;


using namespace boost::python;
	
using namespace cv;

class CTrajectory
{
	public:
	CTrajectory(cv::Point2f pos, float from, float to)
	{
		m_Points.resize(static_cast<int>(to - from+1), cv::Point2f(999999,999999));
		m_Points[0] = pos;
		m_StartIndex = static_cast<int>(from);
	};
	void run(const cv::Mat & flow, int index, float scale, bool verbose)
	{	
		cv::Rect roi(0,0,flow.cols, flow.rows);
		
		int idx = index - m_StartIndex;
		if ( verbose )
		    std::cout << " idx " << idx << " index " <<  index  << "m_StartIndex " << m_StartIndex << " " <<  m_Points.size() <<std::endl;
		if ( idx >= 0 && idx + 1 < m_Points.size())
		{
			cv::Point2f pos = m_Points[idx];
			cv::Point2i ipos(cvFloor(pos.x), cvFloor(pos.y));
			if ( verbose )
		           std::cout << pos << " " << ipos << " " << roi << std::endl;
			if( roi.contains(ipos) && roi.contains(ipos + cv::Point2i(1,1)))
			{
			    if ( verbose )
		            std::cout << " add point " << std::endl;
				float a = pos.x - ipos.x;
				float b = pos.y - ipos.y;
				float iw00 = (1.f - a)*(1.f - b);
				float iw01 = a*(1.f - b);
				float iw10 = (1.f - a)*b;
				float iw11 = 1.f - iw00 - iw01 - iw10;
				m_Points[idx + 1] = pos + (
				flow.at<cv::Point2f>(ipos)*iw00 +
				flow.at<cv::Point2f>(ipos + cv::Point2i(1,0))*iw01 +
                flow.at<cv::Point2f>(ipos + cv::Point2i(0,1))*iw10 +
				flow.at<cv::Point2f>(ipos + cv::Point2i(1,1))*iw11) + cv::Point2f(scale,0);
			}
		}
	}
	std::vector<cv::Point2f> m_Points;
	int m_StartIndex;
	
};
cv::Mat nptocv(np::ndarray src)
{
	if (src.get_nd() != 2 ) 
		throw std::runtime_error("Error Input image type !=2 ");
	if ( (src.get_flags() & np::ndarray::C_CONTIGUOUS) == 0)  
		throw std::runtime_error("Error Input image is not C_CONTIGUOUS ");
	if ( src.get_dtype() != np::dtype::get_builtin<float>() )  
		throw std::runtime_error("Error Input dtype (needed float32)");

	int nochannels = 1;
	int cols = src.shape(1);
	int rows = src.shape(0);
	
	void * src_data = src.get_data();
	cv::Mat data(rows, cols, CV_32FC1, src_data);
	return data.clone();
}


/*
void TrajectoryEstimator::python_set_parameter(boost::python::dict & param)
{

	boost::python::list keys = param.keys(); 
	for (int i = 0; i < len(keys); ++i) 
	{  
	   boost::python::extract<std::string> extracted_key(keys[i]);  
	   if(!extracted_key.check()){  
			std::cout<<"Key invalid, map might be incomplete"<<std::endl;  
			throw(std::runtime_error("Invalid Key"));                 
	   }  
	   std::string key = extracted_key;  
	   boost::python::extract<std::string> extracted_val(param[key]);  
	   if(extracted_val.check())
	   {  
		   parseString(key, extracted_val);
	   }  
	
	}  

}	

void TrajectoryEstimator::parseString(std::string key, std::string val)
{
	std::string upper_val = val;
	std::transform(upper_val.begin(), upper_val.end(), upper_val.begin(), ::toupper);
	std::transform(key.begin(), key.end(), key.begin(), ::toupper);
	if ( key == "MODE")
	{
		m_Mode = boost::lexical_cast<int>(val);
	}
	if ( key == "VERBOSE")
	{
		m_Verbose = boost::lexical_cast<int>(val);
	}
}
*/
py::list TrajectoryEstimator::run(py::list pyOFFilenames, np::ndarray pyPoints, float scale, int verbose)
{
	std::vector<CTrajectory> trajectory_list;
	cv::Mat points = nptocv(pyPoints);
	for( int r = 0; r < points.rows; r++)
	{
		trajectory_list.push_back(CTrajectory(cv::Point2f(points.at<float>(r,3), points.at<float>(r,2)), points.at<float>(r,0), points.at<float>(r,1)));

	}
	std::vector<std::string> of_filenames;
	for( int i = 0 ; i < len(pyOFFilenames); ++i)
	{
		std::string flowFilename = py::extract<std::string>(pyOFFilenames[i]);
		//std::cout << flowFilename << std::endl;
		cv::Mat flow = cv::optflow::readOpticalFlow(flowFilename);
		//std::cout << " Flow Field " << flow.size  << flow.cols << std::endl;
		for( int n = 0; n < trajectory_list.size(); n++)
		{
		    if ( verbose > 0 && n == 0)
			    trajectory_list[n].run(flow, i, scale, 1);
			else
			    trajectory_list[n].run(flow, i, scale, 0);
		}
	}

	py::list result;
	for( int n = 0; n < trajectory_list.size(); n++)
	{
	    py::list pyTrajectory;;
	    for ( auto itr = trajectory_list[n].m_Points.begin(); itr != trajectory_list[n].m_Points.end(); itr++ )
	    {
	        pyTrajectory.append( itr->y );
	        pyTrajectory.append( itr->x );
	    }
	    result.append(pyTrajectory);

	}

	return result;
}
		
	
	