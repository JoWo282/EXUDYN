/** ***********************************************************************************************
* @brief		Includes for basic linalg: Vectors(Slim-/Const-/Resizable-/LinkedData), Matrizes (Const-/Resizable-/LinkedData) and Arrays; 
*				also defines advanced templates for matrix/vector operations
*
* @author		Gerstmayr Johannes
* @date			1997-05-15 (generated)
* @date			2019-05-15 (last modified)
* @copyright    This file is part of Exudyn. Exudyn is free software: you can redistribute it and/or modify it under the terms of the Exudyn license. See "LICENSE.txt" for more details.
* @todo         Vector::operators, check if data[cnt++] works and is faster
*
************************************************************************************************ */

#ifndef BASICLINALG__H
#define BASICLINALG__H

//BasicLinalg provides consistent includes for BasicDefinitions, arrays, vectors and matrices
#include <initializer_list> //for initializer_list in constructor
#include <ostream>
//#include <stdlib.h> //only works in MSVC for initialization with std::vector
#include <array>
#include <vector>
#include "Utilities/ReleaseAssert.h"
#include "Utilities/BasicDefinitions.h" //defines Real
#include "Utilities/BasicFunctions.h"

#include "Utilities/ResizableArray.h"	//includes SlimArray.h and BasicFunctions.h
#include "Linalg/LinkedDataVector.h"	//includes SlimVector.h and Vector.h
#include "Linalg/ResizableVector.h"	//includes SlimVector.h and Vector.h
#include "Linalg/ConstSizeVector.h"	
#include "Linalg/ConstSizeMatrix.h"		//includes Matrix.h
#include "Linalg/ResizableMatrix.h"	
#include "Linalg/LinkedDataMatrix.h"	

typedef ConstSizeMatrix<9> Matrix3D; //will be changed to SlimMatrix<...>
typedef ConstSizeMatrix<4> Matrix2D; //will be changed to SlimMatrix<...>
typedef ConstSizeMatrix<6*6> Matrix6D;//will be changed to SlimMatrix<...>

typedef ConstSizeMatrixBase<float, 9> Matrix3DF; //will be changed to SlimMatrix<...>
typedef ConstSizeMatrixBase<float,4> Matrix2DF; //will be changed to SlimMatrix<...>

//makes problems with Index: typedef ConstSizeMatrixBase<Index, 9> Matrix3DI; //will be changed to SlimMatrix<...>


namespace EXUmath {

#ifndef __APPLE__
	inline static const Matrix3DF unitMatrix3DF(3, 3, { 1.f,0.f,0.f, 0.f,1.f,0.f, 0.f,0.f,1.f });
	inline static const Matrix3D unitMatrix3D(3, 3, { 1.,0.,0., 0.,1.,0., 0.,0.,1. });
	inline static const Matrix3D zeroMatrix3D(3, 3, 0.);
	inline static const MatrixI unitMatrixI(3, 3, { 1,0,0, 0,1,0, 0,0,1 });
	inline static const Vector3D unitVecX({ 1.,0.,0. });
	inline static const Vector3D unitVecY({ 0.,1.,0. });
	inline static const Vector3D unitVecZ({ 0.,0.,1. });
#else
	static const Matrix3DF unitMatrix3DF(3, 3, { 1.f,0.f,0.f, 0.f,1.f,0.f, 0.f,0.f,1.f });
	static const Matrix3D unitMatrix3D(3, 3, { 1.,0.,0., 0.,1.,0., 0.,0.,1. });
	static const Matrix3D zeroMatrix3D(3, 3, 0.);
	static const MatrixI unitMatrixI(3, 3, { 1,0,0, 0,1,0, 0,0,1 });
	static const Vector3D unitVecX({ 1.,0.,0. });
	static const Vector3D unitVecY({ 0.,1.,0. });
	static const Vector3D unitVecZ({ 0.,0.,1. });
#endif

	//! compute sinc(x) = sin(x)/x including case x=0, where sinc(x) = 1
	template <class T>
	inline T Sinc(T x)
	{
		if (x == 0.) { return 1.; }
		else { return sin(x) / x; }
	}

	//! compute cot(x) = 1./tan(x); fails for x=0
	template <class T>
	double Cot(T x) { return(1. / tan(x)); }

	inline Vector3D GetUnitVector(Index i)
	{
		CHECKandTHROW(i < 3, "EXUmath::GetUnitVector: index must be < 3!");
		Vector3D v({ 0.,0.,0. });
		v[i] = 1.;
		return v;
	}

	//convert 3x3 Matrix to std::array<std::array<Real, matrixColumns>, matrixRows>; used mainly for pybind conversion
	template<class TMatrix, Index rows, Index columns, class T>
	inline std::array<std::array<T, rows>, columns> MatrixToStdArrayTemplate(const TMatrix& matrix)
	{
		std::array<std::array<T, columns>, rows> stdarray;
		for (Index i = 0; i < rows; i++) {
			for (Index j = 0; j < columns; j++)
			{
				stdarray[i][j] = matrix(i, j);
			}
		}
		return stdarray;
	}

	//convert Matrix6D to std::array (e.g. used to convert to python)
	inline std::array<std::array<Real, 6>, 6> Matrix6DToStdArray66(const Matrix6D& matrix) {
		return MatrixToStdArrayTemplate<Matrix6D, 6, 6, Real>(matrix);
	}

	//convert Matrix3D to std::array (e.g. used to convert to python)
	inline std::array<std::array<Real, 3>, 3> Matrix3DToStdArray33(const Matrix3D& matrix) {
		return MatrixToStdArrayTemplate<Matrix3D, 3, 3, Real>(matrix);
	}

	//convert Matrix to std::array (e.g. used to convert to python)
	inline std::array<std::array<Real, 3>, 3> MatrixToStdArray33(const Matrix& matrix) {
		return MatrixToStdArrayTemplate<Matrix, 3, 3, Real>(matrix);
	}

	inline std::array<std::array<float, 3>, 3> Matrix3DFToStdArray33(const Matrix3DF& matrix) {
		return MatrixToStdArrayTemplate<Matrix3DF, 3, 3, float>(matrix);
	}

	//convert Vector to std::array<std::array<Real, matrixColumns>, matrixRows>; used mainly for pybind conversion
	template<Index rows, Index columns, class T>
	inline std::array<std::array<T, rows>, columns> VectorToStdArrayArrayTemplate(const SlimVectorBase<T,(Index)(rows*columns)>& vector)
	{
		std::array<std::array<T, columns>, rows> stdarray;
		for (Index i = 0; i < rows; i++) {
			for (Index j = 0; j < columns; j++)
			{
				stdarray[i][j] = vector[i*columns + j];
			}
		}
		return stdarray;
	}

	//inline std::array<std::array<Real, 3>, 3> SlimVector9ToStdArray33(const SlimVector<9>& vector) {
	//	return VectorToStdArrayArrayTemplate<3, 3, Real>(vector);
	//}
	inline std::array<std::array<float, 3>, 3> SlimVectorF9ToStdArray33F(const Float9& vector) {
		return VectorToStdArrayArrayTemplate<3, 3, float>(vector);
	}
	inline std::array<std::array<float, 4>, 4> SlimVectorF16ToStdArray44F(const Float16& vector) {
		return VectorToStdArrayArrayTemplate<4, 4, float>(vector);
	}


	//! apply a 3D rigid-body transformation with a source vector, a destination vector (may be same) and a rotation matrix; transformedPosition = positionOffset + rotation*localPosition
	template<class TMatrix, class TVector>
	inline void RigidBodyTransformation(const TMatrix& rotation, const TVector& positionOffset, const TVector& localPosition, TVector& transformedPosition)
	{
		CHECKandTHROW(rotation.NumberOfRows() == 3 && rotation.NumberOfColumns() == 3 
			&& positionOffset.NumberOfItems() == 3 && localPosition.NumberOfItems() == 3 && transformedPosition.NumberOfItems() == 3, "RigidBodyTransformation: index mismatch");
		
		TVector temp;
		MultMatrixVectorTemplate<TMatrix, TVector, TVector>(rotation, localPosition, temp);
		transformedPosition = positionOffset;
		transformedPosition += temp;
	}

	//! compute orthogonal basis vectors (normal1, normal2) for given vector0 (non-unique solution!); if vector0 == [0,0,0], then any normal basis is returned
	inline void ComputeOrthogonalBasis(Vector3D vector0, Vector3D& normal1, Vector3D& normal2)
	{
		Real L0 = vector0.GetL2Norm();
		if (L0 == 0.) { normal1.SetVector({ 1.,0.,0. }); normal2.SetVector({ 0.,1.,0. }); } //any solution will suffice
		vector0 *= 1. / L0;

		if (fabs(vector0[0]) > 0.5 && fabs(vector0[1]) < 0.1 && fabs(vector0[2]) < 0.1) { normal1.SetVector({ 0., 1., 0. }); }
		else { normal1.SetVector({ 1., 0., 0. }); }

		Real h = normal1 * vector0;
		normal1 -= h * vector0;
		normal1.Normalize();
		normal2 = vector0.CrossProduct(normal1);
	}

	//! Project normal into normal plane of vector (Gram-Schmidt orthogonalization); works for any vector typehaving scalar*vector and vector*vector operator
	template<class TVector>
	inline void GramSchmidtOrthogonalization(const TVector vector, TVector& normal)
	{
		Real h = (normal * vector) / (vector*vector);
		normal -= h * vector;
	}

	//! Use GramSchmidtOrthogonalization(...) and normalize the resulting 'normal' vector; vector must have a .Normalization() function
	template<class TVector>
	inline void GramSchmidtOrthogonalizationNormalized(const TVector vector, TVector& normal)
	{
		GramSchmidtOrthogonalization(vector, normal);
		normal.Normalize();
	}



	//numerical integration in interval [-1,1]; int(1) = 2
	static const SlimVector<1> gaussRuleOrder1Points({ 0. });
	static const SlimVector<1> gaussRuleOrder1Weights({ 2. });
	static const SlimVector<2> gaussRuleOrder3Points({ -sqrt(1. / 3.), sqrt(1. / 3.) });
	static const SlimVector<2> gaussRuleOrder3Weights({ 1., 1. });
	static const SlimVector<3> gaussRuleOrder5Points({ -sqrt(3. / 5.), 0., sqrt(3. / 5.) });
	static const SlimVector<3> gaussRuleOrder5Weights({ 5. / 9., 8. / 9., 5. / 9. });
	static const SlimVector<4> gaussRuleOrder7Points({ -sqrt(3. / 7. + sqrt(120.) / 35.), -sqrt(3. / 7. - sqrt(120.) / 35.), sqrt(3. / 7. - sqrt(120.) / 35.), sqrt(3. / 7. + sqrt(120.) / 35.) });
	static const SlimVector<4> gaussRuleOrder7Weights({ 1. / 2. - 5. / (3.*sqrt(120.)), 1. / 2. + 5. / (3.*sqrt(120.)), 1. / 2. + 5. / (3.*sqrt(120.)), 1. / 2. - 5. / (3.*sqrt(120.)) });
	static const SlimVector<5> gaussRuleOrder9Points({ -0.906179845938664, -0.5384693101056831, 0., 0.5384693101056831, 0.906179845938664 });
	static const SlimVector<5> gaussRuleOrder9Weights({ 0.23692688505618914, 0.47862867049936636, 0.5688888888888889, 0.47862867049936636, 0.23692688505618914 });

	//numerically integrate a function in interval [a,b]
	//inline does not work on older MacOS
#ifndef __APPLE__
	inline auto NumIntegrate = [](Real(*function)(Real), auto& points, auto& weights, Real a, Real b)
	{ 
		Index cnt = 0; Real value = 0.;  
		for (auto item : points) { Real x = 0.5*(b - a)*item + 0.5*(b + a); value += 0.5*(b - a)*weights[cnt++]*function(x); }
	};
#else
	auto NumIntegrate = [](Real(*function)(Real), auto& points, auto& weights, Real a, Real b)
	{
		Index cnt = 0; Real value = 0.;
		for (auto item : points) { Real x = 0.5*(b - a)*item + 0.5*(b + a); value += 0.5*(b - a)*weights[cnt++] * function(x); }
	};
#endif
	//auto function = [](Real x) {return x*x; }; //define a function 

	//+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	//ResizableMatrix/ResizableVector
	inline void MultMatrixVector(const ResizableMatrix& matrix, Vector3D& vector, ResizableVector& result) {
		MultMatrixVectorTemplate<ResizableMatrix, Vector3D, ResizableVector>(matrix, vector, result);
	}

	//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	//Matrix x Vector specialization for different situations:
	inline void MultMatrixVector(const Matrix& matrix, const Vector& vector, Vector& result) {
		MultMatrixVectorTemplate<Matrix, Vector, Vector>(matrix, vector, result);
	}

	inline void MultMatrixVector(const Matrix& matrix, const SlimVector<3>& vector, Vector& result) {
		MultMatrixVectorTemplate<Matrix, SlimVector<3>, Vector>(matrix, vector, result);
	}

	//result as SlimVector not possible (SetNumberOfItems not implemented)
	//inline void MultMatrixVector(const Matrix& matrix, const SlimVector<3>& vector, SlimVector<3>& result) {
	//	MultMatrixVectorTemplate<Matrix, SlimVector<3>, SlimVector<3>>(matrix, vector, result);
	//}

	//for rotation matrix * vector multiplication
	inline void MultMatrixVector(const Matrix& matrix, const ConstSizeVector<3>& vector, Vector& result) {
		MultMatrixVectorTemplate<Matrix, ConstSizeVector<3>, Vector>(matrix, vector, result);
	}
	//for rotation matrix * vector multiplication
	inline void MultMatrixVector(const Matrix& matrix, const ConstSizeVector<3>& vector, ConstSizeVector<3>& result) {
		MultMatrixVectorTemplate<Matrix, ConstSizeVector<3>, ConstSizeVector<3>>(matrix, vector, result);
	}

	//for rotation matrix times LDV:
	inline void MultMatrixVector(const Matrix3D& matrix, const LinkedDataVector& vector, Vector3D& result) {
		MultMatrixVectorTemplate<Matrix3D, LinkedDataVector, Vector3D>(matrix, vector, result);
	}

	//for Euler parameter multiplications with G-matrix:
	inline void MultMatrixVector(const ConstSizeMatrix<12>& matrix, const ConstSizeVector<4>& vector, Vector& result) {
		MultMatrixVectorTemplate<ConstSizeMatrix<12>, ConstSizeVector<4>, Vector>(matrix, vector, result);
	}

	//for Euler parameter multiplications with G-matrix:
	inline void MultMatrixVector(const ConstSizeMatrix<12>& matrix, const ConstSizeVector<4>& vector, ConstSizeVector<3>& result) {
		MultMatrixVectorTemplate<ConstSizeMatrix<12>, ConstSizeVector<4>, ConstSizeVector<3>>(matrix, vector, result);
	}

	//for Euler parameter multiplications with G-matrix:
	inline void MultMatrixVector(const ConstSizeMatrix<12>& matrix, const ConstSizeVector<4>& vector, Vector3D& result) {
		MultMatrixVectorTemplate<ConstSizeMatrix<12>, ConstSizeVector<4>, Vector3D>(matrix, vector, result);
	}

	//for Euler parameter multiplications with G-matrix:
	inline void MultMatrixVector(const ConstSizeMatrix<12>& matrix, const LinkedDataVector& vector, Vector3D& result) {
		MultMatrixVectorTemplate<ConstSizeMatrix<12>, LinkedDataVector, Vector3D>(matrix, vector, result);
	}

	//for Euler parameter multiplications with G^T-matrix:
	inline void MultMatrixVector(const ConstSizeMatrix<12>& matrix, const Vector3D& vector, ConstSizeVector<4>& result) {
		MultMatrixVectorTemplate<ConstSizeMatrix<12>, Vector3D, ConstSizeVector<4>>(matrix, vector, result);
	}

	//for rotation matrix * vector multiplication
	inline void MultMatrixVector(const Matrix3D& matrix, Vector3D& vector, Vector& result) {
		MultMatrixVectorTemplate<Matrix3D, Vector3D, Vector>(matrix, vector, result);
	}
	inline void MultMatrixVector(const Matrix3D& matrix, Vector3D& vector, Vector3D& result) {
		MultMatrixVectorTemplate<Matrix3D, Vector3D, Vector3D>(matrix, vector, result);
	}
	inline void MultMatrixVector(const Matrix3D& matrix, const Vector& vector, Vector3D& result) {
		MultMatrixVectorTemplate<Matrix3D, Vector, Vector3D>(matrix, vector, result);
	}

	//for rigid-body stiffness times displacemnet calculation:
	inline void MultMatrixVector(const ConstSizeMatrix<36>& matrix, const Vector6D& vector, Vector6D& result) {
		MultMatrixVectorTemplate<ConstSizeMatrix<36>, Vector6D, Vector6D>(matrix, vector, result);
	}

	//for ANCFCable-ALE:
	inline void MultMatrixVector(const ConstSizeMatrix<64>& matrix, const CSVector8D& vector, CSVector8D& result) {
		MultMatrixVectorTemplate<ConstSizeMatrix<64>, CSVector8D, CSVector8D>(matrix, vector, result);
	}


	//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	//transposed version of Matrix x Vector:
	inline void MultMatrixTransposedVector(const Matrix& matrix, const Vector& vector, Vector& result) {
		MultMatrixTransposedVectorTemplate<Matrix, Vector, Vector>(matrix, vector, result);
	}

	inline void MultMatrixTransposedVector(const Matrix& matrix, const SlimVector<3>& vector, Vector& result) {
		MultMatrixTransposedVectorTemplate<Matrix, SlimVector<3>, Vector>(matrix, vector, result);
	}

	inline void MultMatrixTransposedVector(const Matrix& matrix, const SlimVector<1>& vector, Vector& result) {
		MultMatrixTransposedVectorTemplate<Matrix, SlimVector<1>, Vector>(matrix, vector, result);
	}

	inline void MultMatrixTransposedVector(const Matrix& matrix, const ConstSizeVector<3>& vector, Vector& result) {
		MultMatrixTransposedVectorTemplate<Matrix, ConstSizeVector<3>, Vector>(matrix, vector, result);
	}

	inline void MultMatrixTransposedVector(const Matrix& matrix, const ConstSizeVector<3>& vector, ConstSizeVector<3>& result) {
		MultMatrixTransposedVectorTemplate<Matrix, ConstSizeVector<3>, ConstSizeVector<3>>(matrix, vector, result);
	}

	//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	//! result += matrix^T*vector (ADD results)
	inline void MultMatrixTransposedVectorAdd(const Matrix& matrix, const SlimVector<3>& vector, Vector& result) {
		MultMatrixTransposedVectorAddTemplate<Matrix, SlimVector<3>, Vector>(matrix, vector, result);
	}

	//! result += matrix*vector (ADD results)
	inline void MultMatrixVectorAdd(const Matrix& matrix, const Vector& vector, Vector& result) {
		MultMatrixVectorAddTemplate<Matrix, Vector, Vector>(matrix, vector, result);
	}

	//! result += matrix*vector (ADD results)
	inline void MultMatrixVectorAdd(const Matrix& matrix, const Vector3D& vector, Vector& result) {
		MultMatrixVectorAddTemplate<Matrix, Vector3D, Vector>(matrix, vector, result);
	}

	//! result += matrix*vector (ADD results)
	inline void MultMatrixVectorAdd(const Matrix3D& matrix, const Vector& vector, Vector& result) {
		MultMatrixVectorAddTemplate<Matrix3D, Vector, Vector>(matrix, vector, result);
	}

	//! result += matrix*vector (ADD results)
	inline void MultMatrixVectorAdd(const Matrix3D& matrix, const Vector3D& vector, Vector& result) {
		MultMatrixVectorAddTemplate<Matrix3D, Vector3D, Vector>(matrix, vector, result);
	}

	//! result += matrix*vector (ADD results)
	inline void MultMatrixVectorAdd(const ConstSizeMatrix<12>& matrix, const Vector& vector, Vector3D& result) {
		MultMatrixVectorAddTemplate<ConstSizeMatrix<12>, Vector, Vector3D>(matrix, vector, result);
	}

	//! result += matrix*vector (ADD results)
	inline void MultMatrixVectorAdd(const ConstSizeMatrix<12>& matrix, const Vector3D& vector, Vector& result) {
		MultMatrixVectorAddTemplate<ConstSizeMatrix<12>, Vector3D, Vector>(matrix, vector, result);
	}


	//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	//! Matrix * Matrix multiplication templates; this should also work with operator* in ConstSizeMatrix<9>
	inline void MultMatrixMatrix(const ConstSizeMatrix<9>& m1, const ConstSizeMatrix<9>& m2, ConstSizeMatrix<9>& result) {
		MultMatrixMatrixTemplate<ConstSizeMatrix<9>, ConstSizeMatrix<9>, ConstSizeMatrix<9>>(m1, m2, result);
	}

	//! Matrix * Matrix multiplication templates for multiplication with rigid body G-matrices
	inline void MultMatrixMatrix(const ConstSizeMatrix<12>& m1, const ConstSizeMatrix<9>& m2, ConstSizeMatrix<12>& result) {
		MultMatrixMatrixTemplate<ConstSizeMatrix<12>, ConstSizeMatrix<9>, ConstSizeMatrix<12>>(m1, m2, result);
	}

	//! Matrix * Matrix multiplication templates for multiplication with rigid body G-matrices
	inline void MultMatrixMatrix(const ConstSizeMatrix<9>& m1, const ConstSizeMatrix<12>& m2, ConstSizeMatrix<12>& result) {
		MultMatrixMatrixTemplate<ConstSizeMatrix<9>, ConstSizeMatrix<12>, ConstSizeMatrix<12>>(m1, m2, result);
	}

	//! Matrix * Matrix multiplication templates e.g. for computation of inertia tensor
	inline void MultMatrixMatrix(const ConstSizeMatrix<12>& m1, const ConstSizeMatrix<12>& m2, ConstSizeMatrix<16>& result) {
		MultMatrixMatrixTemplate<ConstSizeMatrix<12>, ConstSizeMatrix<12>, ConstSizeMatrix<16>>(m1, m2, result);
	}

	//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	//transposed(Matrix)*Matrix:

	//! transposed(Matrix) * Matrix multiplication templates for multiplication with rigid body G-matrices
	inline void MultMatrixTransposedMatrix(const ConstSizeMatrix<12>& m1, const ConstSizeMatrix<9>& m2, ConstSizeMatrix<12>& result) {
		MultMatrixTransposedMatrixTemplate<ConstSizeMatrix<12>, ConstSizeMatrix<9>, ConstSizeMatrix<12>>(m1, m2, result);
	}

	//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	//! apply column-wise a transformation matrix of fixed size (e.g. for a 3xn matrix, multiply with 3x3 rotation matrix A => size=3)
	template<class TMatrix>
	inline void ApplyTransformation33Template(const Matrix3D& transformationMatrix, TMatrix& sourceDestination)
	{
		CHECKandTHROW(3 == sourceDestination.NumberOfRows() && 
			3 == transformationMatrix.NumberOfColumns() && 
			3 == transformationMatrix.NumberOfRows(),
			"ApplyTransformation: transformationMatrix must be square and equal to number of rows of sourceDestination");

		Vector3D temp;
		for (Index i = 0; i < sourceDestination.NumberOfColumns(); i++)
		{
			MultMatrixVector(transformationMatrix, sourceDestination.GetColumnVector(i), temp);
			for (Index j = 0; j < 3; j++)
			{
				sourceDestination(j, i) = temp[j];
			}
		}
	}

	inline void ApplyTransformation33(const Matrix3D& transformationMatrix, ConstSizeMatrix<12>& sourceDestination) {
		ApplyTransformation33Template<ConstSizeMatrix<12>>(transformationMatrix, sourceDestination);
	}


	//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	//for sparse matrices:

	//!Triplets for simple sparse matrix
	//!very much like Eigen, to be compatible in future!
	class Triplet
	{
	public:
		//Triplet() : m_row(0), m_col(0), m_value(0) {}
		Triplet() {}

		Triplet(const Index& row, const Index& col, const Real& value = 0) : m_row(row), m_col(col), m_value(value) {}

		const Index& row() const { return m_row; }
		const Index& col() const { return m_col; }
		const Real& value() const { return m_value; }

		//! in addition to Eigen, we also allow write access to value!
		Real& value() { return m_value; }
	private: //change to protected if derived class wanted (and also set destructor to virtual ...)
		Index m_row, m_col;
		Real m_value;
	};

	//! simple sparse matrix container for simplistic operations
	class SparseTripletMatrix
	{
	private: //change to protected if derived class wanted (and also set destructor to virtual ...)
		ResizableArray<Triplet> sparseTriplets;
		Index numberOfRows;
		Index numberOfColumns;
	public:
		SparseTripletMatrix() : numberOfRows(0), numberOfColumns(0) {}
		SparseTripletMatrix(Index numberOfRowsInit, Index numberOfColumnsInit, const ResizableArray<Triplet>& sparseTripletsInit)
		{
			for (const Triplet& triplet : sparseTripletsInit)
			{
				sparseTriplets.Append(triplet);
			}
		}
		//! set number of rows and columns
		void SetNumberOfRowsAndColumns(Index numberOfRowsInit, Index numberOfColumnsInit)
		{
			numberOfRows = numberOfRowsInit;
			numberOfColumns = numberOfColumnsInit;
		}

		//! const access to triplet list ==> can be used in Eigen::SparseMatrix
		const ResizableArray<Triplet>& GetTriplets() const { return sparseTriplets; }

		//! for swap with GeneralMatrix
		ResizableArray<Triplet>& GetTriplets() { return sparseTriplets; }

		//! add triplet
		void AddTriplet(const Triplet& triplet) { sparseTriplets.Append(triplet); }

		//! get number of columns
		Index NumberOfRows() const { return numberOfRows; }
		//! get number of rows
		Index NumberOfColumns() const { return numberOfColumns; }

		//! set all matrix items to zero (in dense matrix, all entries are set 0, in sparse matrix, the vector of items is erased)
		void SetAllZero() { sparseTriplets.SetNumberOfItems(0); }

		//! reset matrices and free memory
		void Reset() { SetNumberOfRowsAndColumns(0, 0); sparseTriplets.SetMaxNumberOfItems(0); };

		//! multiply either triplets or matrix entries with factor
		void MultiplyWithFactor(Real factor)
		{
			for (auto& item : sparseTriplets)
			{
				item.value() *= factor;
			}
		}

		////! set the matrix with a dense matrix; do not use this function for computational tasks, as it will drop performance significantly
		//void SetMatrix(const Matrix& otherMatrix);

		//! multiply matrix with vector: solution = A*x
		//! this leads to memory allocation in case that the matrix is built from triplets
		void MultMatrixVector(const Vector& x, Vector& solution) const
		{
			solution.SetAll(0.); //! because some values may not be touched, others may be written several times ...

			for (const auto& item : sparseTriplets)
			{
				solution[item.row()] += x[item.col()] * item.value(); //must be "+=", becaues several values may be added!!!!
			}
		}

		//! multiply matrix with vector and add to solution: solution += A*x
		//! this leads to memory allocation in case that the matrix is built from triplets
		void MultMatrixVectorAdd(const Vector& x, Vector& solution) const
		{
			for (const auto& item : sparseTriplets)
			{
				solution[item.row()] += x[item.col()] * item.value();
			}
		}

		////! multiply transposed(matrix) with vector: solution = A^T*x
		////! this leads to memory allocation in case that the matrix is built from triplets
		//virtual void MultMatrixTransposedVector(const Vector& x, Vector& solution);

		//! multiply matrix with vector: solution = *this * matrix
		void MultMatrixDenseMatrix(const Matrix& matrix, Matrix& solution) const
		{
			CHECKandTHROW(NumberOfColumns() == matrix.NumberOfRows(), "SparseTripletMatrix::MultMatrixDenseMatrix: inconsistent matrices!");
			solution.SetNumberOfRowsAndColumns(NumberOfRows(), matrix.NumberOfColumns());
			solution.SetAll(0);

			Index mColumns = matrix.NumberOfColumns();
			for (const auto& item : sparseTriplets)
			{
				for (Index i = 0; i < mColumns; i++)
				{
					solution(item.row(), i) += item.value() * matrix(item.col(), i);
				}
			}
		}

		//! multiply matrix with vector: solution = matrix^T * *this
		void MultDenseMatrixTransposedMatrix(const Matrix& matrix, Matrix& solution) const
		{
			CHECKandTHROW(NumberOfRows() == matrix.NumberOfRows(), "SparseTripletMatrix::MultDenseMatrixTransposedMatrix: inconsistent matrices!");
			solution.SetNumberOfRowsAndColumns(matrix.NumberOfColumns(), NumberOfColumns());
			solution.SetAll(0);

			Index mColumns = matrix.NumberOfColumns();
			for (const auto& item : sparseTriplets)
			{
				for (Index i = 0; i < mColumns; i++)
				{
					solution(i, item.col()) += item.value() * matrix(item.row(), i);
				}
			}
		}

		//! add triplets to given dense matrix, using row and column offset and factor
		void AddToDenseMatrix(Matrix& denseMatrix, Index rowOffset = 0, Index colOffset = 0, Real factor = 1.) const
		{
			if (rowOffset == 0 and colOffset == 0 and factor == 1.)
			{
				for (auto& item : sparseTriplets)
				{
					denseMatrix(item.row(), item.col()) += item.value();
				}
			}
			else
			{
				for (auto& item : sparseTriplets)
				{
					denseMatrix(item.row() + rowOffset, item.col() + colOffset) += factor * item.value();
				}
			}
		}

		//! slow function which returns triplets as matrix
		Matrix GetTripletsAsMatrix() const
		{
			Matrix triplets(sparseTriplets.NumberOfItems(), 3);
			Index cnt = 0;
			for (const Triplet& item : sparseTriplets)
			{
				triplets(cnt, 0) = (Real)item.row();
				triplets(cnt, 1) = (Real)item.col();
				triplets(cnt, 2) = item.value();
				cnt++;
			}
			return triplets;
		}

		//! return a dense matrix from any other matrix: requires a copy - SLOW!
		ResizableMatrix GetEXUdenseMatrix() const
		{
			ResizableMatrix denseMatrix; // (NumberOfRows(), NumberOfColumns());
			Convert2DenseMatrix(denseMatrix);
			//denseMatrix.SetAll(0.);

			//for (auto& item : sparseTriplets)
			//{
			//	denseMatrix(item.row(), item.col()) += item.value();
			//}
			return denseMatrix;
		}

		//! convert to dense matrix without copying (but may create large matrices!)
		void Convert2DenseMatrix(ResizableMatrix& denseMatrix) const
		{
			denseMatrix.SetNumberOfRowsAndColumns(NumberOfRows(), NumberOfColumns());
			denseMatrix.SetAll(0.);

			for (auto& item : sparseTriplets)
			{
				denseMatrix(item.row(), item.col()) += item.value();
			}
		}

		//! function to print matrix
		void PrintMatrix(std::ostream& os) const
		{
			os << GetEXUdenseMatrix();
		}
	};


	//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	//for sparse vectors:

	//!(index,value) tuplets for simple sparse vector
	class IndexValue
	{
	public:
		IndexValue() {}

		IndexValue(const Index& index, const Real& value = 0.) : m_index(index), m_value(value) {}

		const Index& GetIndex() const { return m_index; }
		const Real& GetValue() const { return m_value; }

		//! also allow write access to value:
		Real& GetValue() { return m_value; }

	private: //change to protected if derived class wanted (and also set destructor to virtual ...)
		Index m_index;
		Real m_value;
	};

	//! simple sparse matrix container for simplistic operations
	class SparseVector
	{
	private: //change to protected if derived class wanted (and also set destructor to virtual ...)
		ResizableArray<IndexValue> data;
		Index vectorSize;  //original vector size, if needed
	public:
		SparseVector() : vectorSize(0) {}
		SparseVector(Index vectorSizeInit)
		{
			vectorSize = vectorSizeInit;
		}
		SparseVector(Index vectorSizeInit, const ResizableArray<IndexValue>& sparseIndexValueInit)
		{
			vectorSize = vectorSizeInit;
			data.SetNumberOfItems(sparseIndexValueInit.NumberOfItems());
			for (Index i=0; i < sparseIndexValueInit.NumberOfItems(); i++)
			{
				data[i]=sparseIndexValueInit[i];
			}
		}
		//! set number of rows and columns
		void SetVectorSize(Index vectorSizeInit)
		{
			vectorSize = vectorSizeInit;
		}

		//! const access to triplet list ==> can be used in Eigen::SparseMatrix
		const ResizableArray<IndexValue>& GetSparseIndexValues() const { return data; }

		//! for swap with GeneralMatrix
		ResizableArray<IndexValue>& GetSparseIndexValues() { return data; }

		//! add tuple
		void AddIndexValue(const IndexValue& item) { data.AppendPure(item); }

		//! add tuple
		void AddIndexAndValue(Index index, Real value) { data.AppendPure(IndexValue(index, value)); }

		//! get size of full vector
		Index VectorSize() const { return vectorSize; }

		//! set all matrix items to zero (in dense matrix, all entries are set 0, in sparse matrix, the vector of items is erased)
		void SetAllZero() { data.SetNumberOfItems(0); }

		//! reset matrices and free memory
		void Reset() { SetVectorSize(0); data.SetMaxNumberOfItems(0); };

		//! multiply either triplets or matrix entries with factor
		void MultiplyWithFactor(Real factor)
		{
			for (auto& item : data)
			{
				item.GetValue() *= factor;
			}
		}

		//! add triplets to given dense matrix, using row and column offset and factor
		void AddToDenseVector(Vector& denseVector, Index rowOffset = 0, Real factor = 1.) const
		{
			if (rowOffset == 0 && factor == 1.)
			{
				for (auto& item : data)
				{
					denseVector[item.GetIndex()] += item.GetValue();
				}
			}
			else
			{
				for (auto& item : data)
				{
					denseVector[item.GetIndex() + rowOffset] += factor*item.GetValue();
				}
			}
		}

		//! slow function which returns triplets converted into dense vector
		Vector GetDenseVector() const
		{
			Vector denseVector(VectorSize(), 0.); //zero vector!
			for (const IndexValue& item : data)
			{
				denseVector[item.GetIndex()] += item.GetValue(); //add, because possibly double indices
			}
			return denseVector;
		}


		//! function to print matrix
		void PrintMatrix(std::ostream& os) const
		{
			os << GetDenseVector() << "\n";
		}
	};


}

//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//sparse triplets moved here to simplify usage
typedef EXUmath::Triplet SparseTriplet;						//! this is a simple (row,col,value) structure for sparse matrix non zero entries
typedef ResizableArray<SparseTriplet> SparseTripletVector;	//! this vector stores (dynamically!) the triplets



#endif
