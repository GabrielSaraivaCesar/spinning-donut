# Performance logs
This is temporary log runing the code on my own computer. The idea is to compare them after changes/optimizations 
## Version 1.0
Basic version - No light, no face normals, no backface culling
| 3D Mesh Name | Faces | Average FPS |
|--|--|--|
| Toroid | 400 | 43.82 |
| Toroid | 2500 | 11.59 |
| Cube | 6 | 126.81 |
| Pyramid | 5 | 148.57 |

## Version 1.1
Face normals implemented + light value based on face normals and light source
| 3D Mesh Name | Faces | Average FPS |
|--|--|--|
| Toroid | 400 | 41.34 |
| Toroid | 2500 | 10.50 |
| Cube | 6 | 128.66 |
| Pyramid | 5 | 118.97 |

## Version 1.2
Backface culling implemented
| 3D Mesh Name | Faces | Average FPS |
|--|--|--|
| Toroid | 400 | 74.75 |
| Toroid | 2500 | 18.21 |
| Cube | 6 | 274.60 |
| Pyramid | 5 | 258.52 |