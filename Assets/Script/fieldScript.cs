using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class fieldScript : MonoBehaviour
{
    [HideInInspector]
    public Vector3 rightTop, leftBottom;
    private Vector2 lastScreenSize;
    private GameObject yminObj, xminObj, xmaxObj;
    private Kirurobo.UniWindowController uniwinc;

    private void Awake()
    {
        lastScreenSize = new Vector2(Screen.width, Screen.height);
        yminObj = transform.Find("-y").gameObject;
        xmaxObj = transform.Find("+x").gameObject;
        xminObj = transform.Find("-x").gameObject;
        FitFieldToScreen();
    }

    private void Start()
    {
        uniwinc = GameObject.FindObjectOfType<Kirurobo.UniWindowController>();
        if (uniwinc)
        {
            // Add events
            uniwinc.OnStateChanged += (type) =>
            {
                FitFieldToScreen();
            };
            uniwinc.OnMonitorChanged += () => {
                FitFieldToScreen();
            };
        }
    }

    private void FitFieldToScreen()
    {
        rightTop = Camera.main.ScreenToWorldPoint(new Vector3(Screen.width, Screen.height, 0));
        leftBottom = Camera.main.ScreenToWorldPoint(Vector3.zero);
        // Debug.Log(rightTop);
        // (10.12, 5.00, -10.00)
        // Debug.Log(leftBottom);
        // (-10.12, -5.00, -10.00)

        yminObj.transform.position = new Vector3(
            ((rightTop.x + leftBottom.x) / 2),
            leftBottom.y - 0.5f,
            0
        );
        yminObj.transform.localScale = new Vector3(
            (rightTop.x - leftBottom.x),
            1,
            1
        );

        xminObj.transform.position = new Vector3(
            rightTop.x + 0.5f,
            ((rightTop.y + leftBottom.y) / 2),
            0
        );
        xminObj.transform.localScale = new Vector3(
            1,
            (rightTop.y - leftBottom.y),
            1
        );

        xmaxObj.transform.position = new Vector3(
            leftBottom.x - 0.5f,
            ((rightTop.y + leftBottom.y) / 2),
            0
        );
        xmaxObj.transform.localScale = new Vector3(
            1,
            (rightTop.y - leftBottom.y),
            1
        );
    }

    private void Update()
    {
        Vector2 screenSize = new Vector2(Screen.width, Screen.height);
        if (screenSize != lastScreenSize) FitFieldToScreen();
    }
}
