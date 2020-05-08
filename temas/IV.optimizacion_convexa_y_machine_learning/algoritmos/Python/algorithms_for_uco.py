import math

import numpy as np

from numerical_differentiation import gradient_approximation, \
                                      Hessian_approximation
from line_search import line_search_by_backtracking
from utils import compute_error



def gradient_descent(f, x_0, tol, 
                     tol_backtracking, x_ast=None, p_ast=None, maxiter=30,
                     gf_symbolic=None):
    '''
    Method of gradient descent to numerically approximate solution of min f.
    Args:
        f (fun): definition of function f as lambda expression or function definition.
        x_0 (numpy ndarray): initial point for gradient descent method.
        tol (float): tolerance that will halt method. Controls norm of gradient of f.
        tol_backtracking (float): tolerance that will halt method. Controls value of line search by backtracking.
        x_ast (numpy ndarray): solution of min f, now it's required that user knows the solution...
        p_ast (float): value of f(x_ast), now it's required that user knows the solution...
        maxiter (int): maximum number of iterations.
        gf_symbolic (fun): definition of gradient of f. If given, no approximation is
                                     performed via finite differences.
    Returns:
        x (numpy ndarray): numpy array, approximation of x_ast.
        iteration (int): number of iterations.
        Err_plot (numpy ndarray): numpy array of absolute error between p_ast and f(x) with x approximation
                                  of x_ast. Useful for plotting.
        x_plot (numpy ndarray): numpy array that containts in columns vector of approximations. Last column
                                contains x, approximation of solution. Useful for plotting.
    '''
    iteration = 0
    x = x_0
    
    feval = f(x)
    if gf_symbolic:
        gfeval = gf_symbolic(x)
    else:
        gfeval = gradient_approximation(f,x)

    normgf = np.linalg.norm(gfeval)
    
    Err_plot_aux = np.zeros(maxiter)
    Err_plot_aux[iteration]=compute_error(p_ast,feval)
    
    Err = compute_error(x_ast,x)
    n = x.size
    x_plot = np.zeros((n,maxiter))
    x_plot[:,iteration] = x
    
    print('I\tNormagf\t\tError x_ast\tError p_ast\tline search')
    print('{}\t{:0.2e}\t{:0.2e}\t{:0.2e}\t{}'.format(iteration,normgf,Err,Err_plot_aux[iteration],"---"))
    iteration+=1
    while(normgf>tol and iteration < maxiter):
        dir_desc = -gfeval
        der_direct = gfeval.dot(dir_desc)
        t = line_search_by_backtracking(f,dir_desc,x,der_direct)
        x = x + t*dir_desc
        feval = f(x)
        if gf_symbolic:
            gfeval = gf_symbolic(x)
        else:
            gfeval = gradient_approximation(f,x)
        normgf = np.linalg.norm(gfeval)
        Err_plot_aux[iteration]=compute_error(p_ast,feval)
        x_plot[:,iteration] = x
        Err = compute_error(x_ast,x)
        print('{}\t{:0.2e}\t{:0.2e}\t{:0.2e}\t{:0.2e}'.format(iteration,normgf,Err,
                                                                      Err_plot_aux[iteration],t))
        if t<tol_backtracking: #if t is less than tol_backtracking then we need to check the reason
            iter_salida=iteration
            iteration = maxiter - 1
        iteration+=1
    print('{} {:0.2e}'.format("Error of x with respect to x_ast:",Err))
    print('{} {}'.format("Approximate solution:", x))
    cond = Err_plot_aux > np.finfo(float).eps*10**(-2)
    Err_plot = Err_plot_aux[cond]
    if iteration == maxiter and t < tol_backtracking:
        print("Backtracking value less than tol_backtracking, check approximation")
        iteration=iter_salida
        x_plot = x_plot[:,:iteration]
    else:
        x_plot = x_plot[:,:iteration]
    return [x,iteration,Err_plot,x_plot]

def Newtons_method(f, x_0, tol, 
                   tol_backtracking, x_ast=None, p_ast=None, maxiter=30,
                   gf_symbolic=None,
                   Hf_symbolic=None):
    '''
    Newton's method to numerically approximate solution of min f.
    Args:
        f (fun): definition of function f as lambda expression or function definition.
        x_0 (numpy ndarray): initial point for Newton's method.
        tol (float): tolerance that will halt method. Controls stopping criteria.
        tol_backtracking (float): tolerance that will halt method. Controls value of line search by backtracking.
        x_ast (numpy ndarray): solution of min f, now it's required that user knows the solution...
        p_ast (float): value of f(x_ast), now it's required that user knows the solution...
        maxiter (int): maximum number of iterations
        gf_symbolic (fun): definition of gradient of f. If given, no approximation is
                                     performed via finite differences.
        Hf_symbolic (fun): definition of Hessian of f. If given, no approximation is
                                     performed via finite differences.
    Returns:
        x (numpy ndarray): numpy array, approximation of x_ast.
        iteration (int): number of iterations.
        Err_plot (numpy ndarray): numpy array of absolute error between p_ast and f(x) with x approximation
                          of x_ast. Useful for plotting.
        x_plot (numpy ndarray): numpy array that containts in columns vector of approximations. Last column
                        contains x, approximation of solution. Useful for plotting.
    '''
    iteration = 0
        
    x = x_0
    
    feval = f(x)
    if gf_symbolic:
        gfeval = gf_symbolic(x)
    else:
        gfeval = gradient_approximation(f,x)

    if Hf_symbolic:
        Hfeval = Hf_symbolic(x)
    else:
        Hfeval = Hessian_approximation(f,x)
        
    
    normgf = np.linalg.norm(gfeval)
    condHf= np.linalg.cond(Hfeval)
    
    Err_plot_aux = np.zeros(maxiter)
    Err_plot_aux[iteration]=compute_error(p_ast,feval)
    
    Err = compute_error(x_ast,x)
    n = x.size
    x_plot = np.zeros((n,maxiter))
    x_plot[:,iteration] = x
    
    #Newton's direction and Newton's decrement
    
    dir_Newton = np.linalg.solve(Hfeval, -gfeval)
    dec_Newton = -gfeval.dot(dir_Newton)
    
    print('I\tNormgf \tNewton Decrement\tError x_ast\tError p_ast\tline search\tCondHf')
    print('{}\t{:0.2e}\t{:0.2e}\t{:0.2e}\t{:0.2e}\t{}\t\t{:0.2e}'.format(iteration,normgf,
                                                                         dec_Newton,Err,
                                                                         Err_plot_aux[iteration],"---",
                                                                         condHf))
    stopping_criteria = dec_Newton/2
    iteration+=1
    while(stopping_criteria>tol and iteration < maxiter):
        der_direct = -dec_Newton
        t = line_search_by_backtracking(f,dir_Newton,x,der_direct)
        x = x + t*dir_Newton
        feval = f(x)
        
        if gf_symbolic:
            gfeval = gf_symbolic(x)
        else:
            gfeval = gradient_approximation(f,x)
        
        if Hf_symbolic:
            Hfeval = Hf_symbolic(x)
        else:
            Hfeval = Hessian_approximation(f,x)
        
        normgf = np.linalg.norm(gfeval)
        condHf= np.linalg.cond(Hfeval)
        #Newton's direction and Newton's decrement

        dir_Newton = np.linalg.solve(Hfeval, -gfeval)
        dec_Newton = -gfeval.dot(dir_Newton)
        Err_plot_aux[iteration]=compute_error(p_ast,feval)
        x_plot[:,iteration] = x
        Err = compute_error(x_ast,x)
        print('{}\t{:0.2e}\t{:0.2e}\t{:0.2e}\t{:0.2e}\t{:0.2e}\t{:0.2e}'.format(iteration,normgf,
                                                                                dec_Newton,Err,
                                                                                Err_plot_aux[iteration],t,
                                                                                condHf))
        stopping_criteria = dec_Newton/2
        if t<tol_backtracking: #if t is less than tol_backtracking then we need to check the reason
            iter_salida=iteration
            iteration = maxiter - 1
        iteration+=1
    print('{} {:0.2e}'.format("Error of x with respect to x_ast:",Err))
    print('{} {}'.format("Approximate solution:", x))
    cond = Err_plot_aux > np.finfo(float).eps*10**(-2)
    Err_plot = Err_plot_aux[cond]
    if iteration == maxiter and t < tol_backtracking:
        print("Backtracking value less than tol_backtracking, check approximation")
        iteration=iter_salida
        x_plot = x_plot[:,:iteration]
    else:
        x_plot = x_plot[:,:iteration]
    return [x,iteration,Err_plot,x_plot]