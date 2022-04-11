using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class setPositionZeroScript : MonoBehaviour
{
    Vector3 position;
    // Start is called before the first frame update
    void Start()
    {
        position = transform.position;
        position.z = 0;
        transform.position = position;
    }

    // Update is called once per frame
    void LateUpdate()
    {
        position = transform.position;
        position.z = 0;
        transform.position = position;
    }
}
