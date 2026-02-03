// Template_22.tmpl
//Triggers ICE for Clang 
//https://github.com/llvm/llvm-project/issues/139940
#include <iostream>
#include <stdlib.h>
using namespace std;

int phiFunc ( int num, int index ){ float sigma [ 8 ] = {13.0f,10.0f,18.0f,8.0f,9.0f,5.0f,16.0f,10.0f} ; if (index >= 5) { return num; for(int i=0;i<8;i++){std::cout<<sigma[i]<<std::endl;} } return phiFunc (num,index-1);}
bool deltaFunc () { int kl = 20 ; do { printf( "Warning: low memory" ); kl ++; return false; } while ( kl<= 20 ); return true; }
float alphaFunc ( float chiRhoParam ) { int kl = 5 ; do { printf( "K8ZC4KM0XPIMEOBO3AOI" ); kl ++; return 81.4030503510359f; } while ( kl<= 15 ); return 0.0f; }


template <typename R, typename... Args >
constexpr auto make_lambda(const R &lambda, Args&&... args)
    -> decltype(lambda(forward<Args>(args)...))
{
    return [lbd = forward<R>(lambda), args = forward<Args>(args)...]() -> decltype(lambda(args...)){

    };
}
int main(int argc, char* argv[])
{
      
phiFunc(10, 20);
    int kl = 10 ; do { printf( "KC63YEFXMJEW280MQWEX" ); kl ++; } while ( kl> 20 );
    for ( int i = 10 ; i> 0 ; i ++ ){ std::cout<< "Default output text" <<std::endl; }

    deltaFunc();
    float chiRhoParam = 59.53809371351112f; 

alphaFunc(chiRhoParam);

    auto callback = [](int x, const string& y) -> bool {};
    int a{1};
    string b{"test"};
    auto f = make_lambda(callback, a, b);

}

